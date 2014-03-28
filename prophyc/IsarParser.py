# -*- coding: utf-8 -*-

import xml.dom.minidom
from collections import OrderedDict
from DataHolder import MemberHolder, MessageHolder, DataHolder, UnionHolder, sort_struct

class IsarParser(object):

    primitive_types = {"8 bit integer unsigned": "u8",
                       "16 bit integer unsigned": "u16",
                       "32 bit integer unsigned": "u32",
                       "64 bit integer unsigned": "u64",
                       "8 bit integer signed": "i8",
                       "16 bit integer signed": "i16",
                       "32 bit integer signed": "i32",
                       "64 bit integer signed": "i64",
                       "32 bit float": "r32",
                       "64 bit float": "r64"}

    tmp_dict = OrderedDict()
    typedef_dict = {}
    enum_dict = {}
    constant_dict = {}
    class_aprot_string = "aprot."

    def __struct_parse(self, tree_node, element_name):
        list = []
        struct_nodes = tree_node.getElementsByTagName(element_name)
        for p in struct_nodes:
            if p.hasChildNodes():
                msg = MessageHolder()
                msg.name = p.attributes["name"].value
                member = p.getElementsByTagName('member')
                for k in member:
                    msg.members.extend(self.__checkin_member_fields(k))
                list.append(msg)
        return list

    def __checkin_member_fields(self, k):
        members = []
        member = MemberHolder(k.attributes["name"].value, k.attributes["type"].value)
        if k.hasChildNodes() and k.getElementsByTagName('dimension'):
            dimension = k.getElementsByTagName('dimension')
            for item , dim_val in dimension[0].attributes.items():
                if 'Comment' not in item:
                    member.add_to_list(item, dim_val)
            dimension_tags = dict(dimension[0].attributes.items())

            if "isVariableSize" in dimension_tags:
                if "variableSizeFieldType" in dimension_tags:
                    type = dimension_tags["variableSizeFieldType"]
                else:
                    type = "u32"
                if "variableSizeFieldName" in dimension_tags:
                    name = dimension_tags["variableSizeFieldName"]
                else:
                    name = member.name + "_len"
                members.append(MemberHolder(name, type))
                member.array = True
                member.array_bound = name
                member.array_size = None
            elif "size" in dimension_tags:
                member.array = True
                member.array_bound = None
                member.array_size = dimension_tags["size"]

        members.append(member)
        return members

    def __get_enum_member(self, elem):
        value = elem.getAttribute('value')
        value = value if value != "-1" else "0xFFFFFFFF"
        return (elem.attributes["name"].value, value)

    def __get_enum(self, elem):
        if not elem.hasChildNodes():
            return None
        name = elem.attributes["name"].value
        enumerators = [self.__get_enum_member(member) for member in elem.getElementsByTagName('enum-member')]
        return (name, enumerators)

    def __get_enums(self, dom):
        return dict(filter(None, (self.__get_enum(elem) for elem in dom.getElementsByTagName('enum'))))

    def __union_parse(self, tree_node):
        union_dict = {}
        enum_dict = {}

        union_nodes = tree_node.getElementsByTagName('union')
        for union_element in union_nodes:
            name = union_element.getAttribute('name')
            union = UnionHolder()
            enum = []
            member = union_element.getElementsByTagName("member")
            for member_union_element in member:
                discriminatorValue = member_union_element.getAttribute('discriminatorValue')
                member_type = member_union_element.getAttribute('type')
                member_name = member_union_element.getAttribute('name')
                union.add_to_list(member_type, member_name)
                enum.append(("EDisc" + name + "_" + member_name + "_" + discriminatorValue, discriminatorValue))
            union_dict[name] = union
            enum_dict["EDisc" + name] = enum
        return union_dict, enum_dict

    def __get_typedef(self, elem):
        if elem.hasAttribute("type"):
            return (elem.attributes["name"].value, elem.attributes["type"].value)
        elif elem.hasAttribute("primitiveType"):
            type = self.primitive_types[elem.attributes["primitiveType"].value]
            return ((elem.attributes["name"].value, type))

    def __get_typedefs(self, dom):
        return filter(None, (self.__get_typedef(elem) for elem in dom.getElementsByTagName('typedef')))

    def __sort_constants(self, list):
        primitive = filter(lambda constant: constant[1].isdigit(), list)
        complex = filter(lambda constant: not constant[1].isdigit(), list)
        return primitive + complex

    def __get_constant(self, elem):
        return (elem.attributes["name"].value, elem.attributes["value"].value)

    def __get_constants(self, dom):
        return self.__sort_constants([self.__get_constant(elem) for elem in dom.getElementsByTagName('constant')])

    def __get_includes(self, dom):
        return [elem.attributes["href"].value.split('.')[0] for elem in dom.getElementsByTagName("xi:include")]

    def __parse_tree_node(self, tree_node):
        data_holder = DataHolder()
        data_holder.constants = self.__get_constants(tree_node)
        data_holder.typedefs = self.__get_typedefs(tree_node)
        data_holder.enums = self.__get_enums(tree_node).items()
        data_holder.msgs_list = self.__struct_parse(tree_node, "message")
        data_holder.struct_list = sort_struct(self.__struct_parse(tree_node, "struct"))
        data_holder.includes = self.__get_includes(tree_node)
        data_holder.union_dict, temp_dict = self.__union_parse(tree_node)
        data_holder.enums += temp_dict.items()
        return data_holder

    def parse_string(self, string):
        return self.__parse_tree_node(xml.dom.minidom.parseString(string))

    def parse(self, file):
        return self.__parse_tree_node(xml.dom.minidom.parse(file))
