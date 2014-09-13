#include <vector>
#include <gtest/gtest.h>
#include "generated/Paddings.pp.hpp"

using namespace testing;

TEST(generated_paddings, Endpad)
{
    std::vector<char> data(1024);

    Endpad x;
    x.x = 1;
    x.y = 2;
    size_t size = x.encode(data.data());

    EXPECT_EQ(4, size);
    EXPECT_EQ(std::string(
            "\x01\x00\x02" "\x00",
            size), std::string(data.data(), size));
}

TEST(generated_paddings, EndpadFixed)
{
    std::vector<char> data(1024);

    EndpadFixed x;
    x.x = 1;
    x.y[0] = 2;
    x.y[1] = 3;
    x.y[2] = 4;
    size_t size = x.encode(data.data());

    EXPECT_EQ(8, size);
    EXPECT_EQ(std::string(
            "\x01\x00\x00\x00\x02\x03\x04" "\x00",
            size), std::string(data.data(), size));
}

TEST(generated_paddings, EndpadDynamic)
{
    std::vector<char> data(1024);

    EndpadDynamic x;
    x.x.push_back(2);
    size_t size = x.encode(data.data());

    EXPECT_EQ(8, size);
    EXPECT_EQ(std::string(
            "\x01\x00\x00\x00\x02" "\x00\x00\x00",
            size), std::string(data.data(), size));
}

TEST(generated_paddings, EndpadLimited)
{
    std::vector<char> data(1024);

    EndpadLimited x;
    x.x.push_back(2);
    size_t size = x.encode(data.data());

    EXPECT_EQ(8, size);
    EXPECT_EQ(std::string(
            "\x01\x00\x00\x00\x02" "\x00\x00\x00",
            size), std::string(data.data(), size));
}

TEST(generated_paddings, EndpadGreedy)
{
    std::vector<char> data(1024);

    EndpadGreedy x;
    x.x = 1;
    x.y.push_back(2);
    size_t size = x.encode(data.data());

    EXPECT_EQ(8, size);
    EXPECT_EQ(std::string(
            "\x01\x00\x00\x00\x02" "\x00\x00\x00",
            size), std::string(data.data(), size));
}

TEST(generated_paddings, Scalarpad)
{
    std::vector<char> data(1024);

    Scalarpad x;
    x.x = 1;
    x.y = 2;
    size_t size = x.encode(data.data());

    EXPECT_EQ(4, size);
    EXPECT_EQ(std::string(
            "\x01" "\x00" "\x02\x00",
            size), std::string(data.data(), size));
}

TEST(generated_paddings, ScalarpadComppre)
{
    std::vector<char> data(1024);

    ScalarpadComppre x;
    x.x.x = 1;
    x.y = 2;
    size_t size = x.encode(data.data());

    EXPECT_EQ(4, size);
    EXPECT_EQ(std::string(
            "\x01" "\x00" "\x02\x00",
            size), std::string(data.data(), size));
}

TEST(generated_paddings, ScalarpadComppost)
{
    std::vector<char> data(1024);

    ScalarpadComppost x;
    x.x = 1;
    x.y.x = 2;
    size_t size = x.encode(data.data());

    EXPECT_EQ(4, size);
    EXPECT_EQ(std::string(
            "\x01" "\x00" "\x02\x00",
            size), std::string(data.data(), size));
}

TEST(generated_paddings, UnionpadOptionalboolpad)
{
    std::vector<char> data(1024);

    UnionpadOptionalboolpad x;
    x.x = 1;
    x.has_y = true;
    x.y = 2;
    size_t size = x.encode(data.data());

    EXPECT_EQ(12, size);
    EXPECT_EQ(std::string(
            "\x01" "\x00\x00\x00"
            "\x01\x00\x00\x00"
            "\x02" "\x00\x00\x00",
            size), std::string(data.data(), size));
}

TEST(generated_paddings, UnionpadOptionalvaluepad)
{
    std::vector<char> data(1024);

    UnionpadOptionalvaluepad x;
    x.has_x = true;
    x.x = 2;
    size_t size = x.encode(data.data());

    EXPECT_EQ(16, size);
    EXPECT_EQ(std::string(
            "\x01\x00\x00\x00" "\x00\x00\x00\x00"
            "\x02\x00\x00\x00\x00\x00\x00\x00",
            size), std::string(data.data(), size));
}

TEST(generated_paddings, UnionpadDiscpad)
{
    std::vector<char> data(1024);

    UnionpadDiscpad x;
    x.x = 1;
    x.y.discriminator = UnionpadDiscpad_Helper::discriminator_a;
    x.y.a = 2;
    size_t size = x.encode(data.data());

    EXPECT_EQ(12, size);
    EXPECT_EQ(std::string(
            "\x01" "\x00\x00\x00"
            "\x01\x00\x00\x00"
            "\x02" "\x00\x00\x00",
            size), std::string(data.data(), size));
}

TEST(generated_paddings, UnionpadArmpad)
{
    std::vector<char> data(1024);

    UnionpadArmpad x;
    x.x = 1;
    x.y.discriminator = UnionpadArmpad_Helper::discriminator_a;
    x.y.a = 2;
    size_t size = x.encode(data.data());

    EXPECT_EQ(24, size);
    EXPECT_EQ(std::string(
            "\x01" "\x00\x00\x00\x00\x00\x00\x00"
            "\x01\x00\x00\x00" "\x00\x00\x00\x00"
            "\x02" "\x00\x00\x00\x00\x00\x00\x00",
            size), std::string(data.data(), size));
}