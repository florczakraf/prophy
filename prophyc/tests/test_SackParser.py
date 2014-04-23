import tempfile
import SackParser

def parse(content):
    with tempfile.NamedTemporaryFile(suffix = '.hpp') as temp:
        temp.write(content)
        temp.flush()
        return SackParser.SackParser().parse(temp.name)

def test_simple_struct():
    hpp = """\
#include <stdint.h>
struct X
{
    uint32_t a;
    uint32_t b;
    uint32_t c;
};
"""
    nodes = parse(hpp)

    assert [("X", [("a", "u32", None, None, None, None),
                   ("b", "u32", None, None, None, None),
                   ("c", "u32", None, None, None, None)])] == nodes

def test_ints():
    hpp = """\
#include <stdint.h>
struct X
{
    uint8_t a;
    uint16_t b;
    uint32_t c;
    uint64_t d;
    int8_t e;
    int16_t f;
    int32_t g;
    int64_t h;
    unsigned char i;
    char j;
    signed char k;
    unsigned long l;
    long m;
    void* n;
    float o;
    double p;
};
"""
    nodes = parse(hpp)

    assert [("X", [("a", "u8", None, None, None, None),
                   ("b", "u16", None, None, None, None),
                   ("c", "u32", None, None, None, None),
                   ("d", "u64", None, None, None, None),
                   ("e", "i8", None, None, None, None),
                   ("f", "i16", None, None, None, None),
                   ("g", "i32", None, None, None, None),
                   ("h", "i64", None, None, None, None),
                   ("i", "u8", None, None, None, None),
                   ("j", "i8", None, None, None, None),
                   ("k", "i8", None, None, None, None),
                   ("l", "u32", None, None, None, None),
                   ("m", "i32", None, None, None, None),
                   ("n", "u32", None, None, None, None),
                   ("o", "r32", None, None, None, None),
                   ("p", "r64", None, None, None, None)])] == nodes

def test_nested_typedefs():
    hpp = """\
typedef int my_int;
typedef my_int i_like_typedefs;
typedef i_like_typedefs i_really_do;
struct X
{
    i_really_do a;
};
"""
    nodes = parse(hpp)

    assert [("X", [("a", "i32", None, None, None, None)])] == nodes

# struct typedefed
# struct with struct (in namespace, typedefed)
# struct with nested typedefs
# struct with all ints
# struct with array
# struct with enum
# struct with union
