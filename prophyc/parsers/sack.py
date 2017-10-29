import os
import re
import ctypes.util
from .clang.cindex import Config, Index, CursorKind, TypeKind, TranslationUnitLoadError, LibclangError

from prophyc import model

unambiguous_builtins = {
    TypeKind.UCHAR: 'u8',
    TypeKind.SCHAR: 'i8',
    TypeKind.CHAR_S: 'i8',
    TypeKind.POINTER: 'u32',
    TypeKind.FLOAT: 'r32',
    TypeKind.DOUBLE: 'r64',
    TypeKind.BOOL: 'i32'
}

def alphanumeric_name(cursor):
    name = cursor.type.spelling.decode()
    if name.startswith('struct '):
        name = name.replace('struct ', '', 1)
    elif name.startswith('enum '):
        name = name.replace('enum ', '', 1)
    elif name.startswith('union '):
        name = name.replace('union ', '', 1)
    return re.sub('[^0-9a-zA-Z_]+', '__', name)

def get_enum_member(cursor):
    name = cursor.spelling.decode()
    value = cursor.enum_value
    if value < 0:
        value = "0x%X" % (0x100000000 + value)
    else:
        value = str(value)
    return model.EnumMember(name, value)

class Builder(object):
    def __init__(self, included_isar_supples=[]):
        self.known = set()
        self.nodes = []
        for node in included_isar_supples:
            self._add_node(node)

    def _add_node(self, node):
        self.known.add(node.name)
        self.nodes.append(node)

    def _get_field_array_len(self, tp):
        if tp.kind is TypeKind.CONSTANTARRAY:
            return tp.element_count
        return None

    def _build_field_type_name(self, tp):
        decl = tp.get_declaration()

        if tp.kind is TypeKind.TYPEDEF:
            return self._build_field_type_name(decl.underlying_typedef_type)
        elif tp.kind in (TypeKind.UNEXPOSED, TypeKind.ELABORATED, TypeKind.RECORD):
            if decl.kind in (CursorKind.STRUCT_DECL, CursorKind.CLASS_DECL):
                name = alphanumeric_name(decl)
                if name not in self.known:
                    self.add_struct(decl)
                return name
            elif decl.kind is CursorKind.UNION_DECL:
                name = alphanumeric_name(decl)
                if name not in self.known:
                    self.add_union(decl)
                return name
            elif decl.kind is CursorKind.ENUM_DECL:
                return self._build_field_type_name(decl.type)
            elif decl.kind is CursorKind.TYPEDEF_DECL:
                return self._build_field_type_name(decl.underlying_typedef_type)
            else:
                raise Exception("Unknown declaration")
        elif tp.kind in (TypeKind.CONSTANTARRAY, TypeKind.INCOMPLETEARRAY):
            return self._build_field_type_name(tp.element_type)
        elif tp.kind is TypeKind.ENUM:
            name = alphanumeric_name(decl)
            if name not in self.known:
                self.add_enum(decl)
            return name

        if tp.kind in (TypeKind.USHORT, TypeKind.UINT, TypeKind.ULONG, TypeKind.ULONGLONG):
            return 'u%d' % (tp.get_size() * 8)
        elif tp.kind in (TypeKind.SHORT, TypeKind.INT, TypeKind.LONG, TypeKind.LONGLONG):
            return 'i%d' % (tp.get_size() * 8)

        return unambiguous_builtins[tp.kind]

    def _build_struct_member(self, cursor):
        name = cursor.spelling.decode()
        type_name = self._build_field_type_name(cursor.type)
        array_len = self._get_field_array_len(cursor.type)
        return model.StructMember(name, type_name, size=array_len)

    def _build_union_member(self, cursor, disc):
        name = cursor.spelling.decode()
        type_name = self._build_field_type_name(cursor.type)
        return model.UnionMember(name, type_name, str(disc))

    def add_enum(self, cursor):
        members = list(map(get_enum_member, cursor.get_children()))
        node = model.Enum(alphanumeric_name(cursor), members)
        self._add_node(node)

    def add_struct(self, cursor):
        members = [self._build_struct_member(x)
                   for x in cursor.get_children()
                   if x.kind is CursorKind.FIELD_DECL and not x.is_bitfield()]
        node = model.Struct(alphanumeric_name(cursor), members)
        self._add_node(node)

    def add_union(self, cursor):
        members = [self._build_union_member(x, i)
                   for i, x in enumerate(cursor.get_children())
                   if x.kind is CursorKind.FIELD_DECL]
        node = model.Union(alphanumeric_name(cursor), members)
        self._add_node(node)

def build_model(tu, isar_supples=[]):
    builder = Builder(isar_supples)
    for cursor in tu.cursor.get_children():
        if cursor.kind is CursorKind.UNEXPOSED_DECL:
            for in_cursor in cursor.get_children():
                if in_cursor.kind is CursorKind.STRUCT_DECL and in_cursor.spelling and in_cursor.is_definition():
                    builder.add_struct(in_cursor)
        if cursor.spelling and cursor.is_definition():
            if cursor.kind is CursorKind.STRUCT_DECL:
                builder.add_struct(cursor)
            if cursor.kind is CursorKind.ENUM_DECL:
                builder.add_enum(cursor)
    if isar_supples:
        cheated_names = list(get_node_names(isar_supples))
        builder.nodes = [n for n in builder.nodes if n.name not in cheated_names]
    return builder.nodes

def _get_location(location):
    return '%s:%s:%s' % (location.file.name.decode(), location.line, location.column)

def _setup_libclang():
    if os.environ.get('PROPHY_NOCLANG'):
        Config.set_library_file('prophy_noclang')
        return

    versions = [None, '3.5', '3.4', '3.3', '3.2', '3.6', '3.7', '3.8', '3.9']
    for v in versions:
        name = v and 'clang-' + v or 'clang'
        libname = ctypes.util.find_library(name)
        if libname:
            Config.set_library_file(libname)
            break

def _check_libclang():
    testconf = Config()
    try:
        testconf.get_cindex_library()
        return True
    except LibclangError:
        return False

def get_node_names(nodes_list):
    for elem in nodes_list:
        if isinstance(elem, model.Include):
            for node in get_node_names(elem.nodes):
                yield node
        else:
            yield elem.name

class SackParserStatus(object):
    def __init__(self, error=None):
        self.error = error

    def __bool__(self):
        return not bool(self.error)

    __nonzero__ = __bool__

class SackParser(object):
    @staticmethod
    def check():
        import platform
        if platform.python_implementation() == 'PyPy':
            return SackParserStatus("sack input doesn't work under PyPy due to ctypes incompatibilities")
        if not _check_libclang():
            return SackParserStatus("sack input requires libclang and it's not installed")
        return SackParserStatus()

    def __init__(self, include_dirs=[], warn=None, supple_nodes=[]):
        self.include_dirs = include_dirs
        self.warn = warn
        self.supple_nodes = supple_nodes
        if supple_nodes:
            self.prepare_clang_fakery(supple_nodes)

    def prepare_clang_fakery(self, supple_nodes):
        import tempfile
        from prophyc.generators.cpp import _generate_def_enum

        def get_nodes_(nodes):
            for node in nodes:
                if isinstance(node, model.Include):
                    for sub_node in get_nodes_(node.nodes):
                        yield sub_node
                else:
                    yield node

        def get_nodes_included_from_isar():
            """ In case of several files including the same root file, is better to get only unique nodes """
            known = []
            for node in get_nodes_(supple_nodes):
                if node.name not in known:
                    known.append(node.name)
                    yield node
        isar_nodes = list(get_nodes_included_from_isar())
        model.topological_sort(isar_nodes)

        def make_cheat(node):
            if isinstance(node, model.Constant):
                return '#define %s %s' % (node.name, node.value)
            if isinstance(node, model.Enum):
                return _generate_def_enum(node)
            else:
                return 'struct %s {};' % node.name

        fakery = '\n'.join(map(make_cheat, isar_nodes))
        self.supple_dir = tempfile.mkdtemp(prefix="prophy_isar_supples_")

        """ TODO: that file created each time the SackParser object is created. """
        fakery_path = os.path.join(self.supple_dir, "isar_supplementary_defs.h")
        with open(fakery_path, 'wt') as f:
            f.write(fakery)
        return fakery

    def parse(self, content, path, _):
        args_ = ["-I" + x for x in self.include_dirs]

        if self.supple_nodes:
            """ Note that line numbers in clang's errors and warnings will be shifted by 1."""
            args_.append(("-I" + self.supple_dir).encode())
            content = '#include "isar_supplementary_defs.h"\n' + content

        index = Index.create()
        path = path.encode()
        content = content.encode()

        try:
            tu = index.parse(path, args_, unsaved_files=((path, content),))
        except TranslationUnitLoadError:
            raise model.ParseError([(path.decode(), 'error parsing translation unit')])
        if self.warn:
            for diag in tu.diagnostics:
                self.warn(diag.spelling.decode(), location=_get_location(diag.location))
        return build_model(tu, self.supple_nodes)


_setup_libclang()
