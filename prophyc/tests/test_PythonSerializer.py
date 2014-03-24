# -*- coding: utf-8 -*-

import sys
import hashlib
import Serializers
import data_holder
import Parser
import pytest
from xml.dom import minidom

linux_hashes = {
"test_of_PythonSerializer" : "5c2d6d350fdea2c825ed8e8fcd875f10",
"test_of_PythonSerializer_enum" : "26f524cefc1243e04e18bbee34eac884",
"test_of_PythonSerializer_import" : "da45c13ad54818957c1b932d8beb56f4"
}

windows_hashes = {
"test_of_PythonSerializer" : "a9fffd7aba64ff037d3cc388f57d7055",
"test_of_PythonSerializer_enum" : "5fb04afd8d7277825823a9ab4247fc68",
"test_of_PythonSerializer_import" : "79981762690c9840a25cb339d87b87bd"
}

hashes = linux_hashes if sys.platform == "linux2" else windows_hashes

@pytest.mark.skipif(True, reason = "why does this test compare hashes? What's the intent?")
def test_of_PythonSerializer():

    ih = data_holder.IncludeHolder()
    th = data_holder.TypeDefHolder()

    for x in range(20, 400, 60):
        ih.add_to_list("test_include_" + str(x))
        th.add_to_list("td_elem_name_" + str(x), "td_elem_val_" + str(x))
        th.add_to_list("td_elem_name_" + str(x), "i_td_elem_val_" + str(x))
        th.add_to_list("td_elem_name_" + str(x), "u_td_elem_val_" + str(x))

    enum = data_holder.EnumHolder()
    for x in range(1, 200, 30):
        enum.add_to_list("elem_" + str(x), "val_" + str(x))

    const = data_holder.ConstantHolder()
    const.add_to_list("C_A", "5")
    const.add_to_list("C_B", "5")
    const.add_to_list("C_C", "C_B + C_A")

    msg_h = data_holder.MessageHolder()
    msg_h.name = "MAC_L2CallConfigResp"
    msg_h.add_to_list(data_holder.MemberHolder('messageResult', 'SMessageResult'))

    dh = data_holder.DataHolder(include = ih, typedef = th , constant = const, msgs_list = [msg_h])
    dh.enum_dict["test"] = enum

    ps = Serializers.get_serializer()
    o = ps.serialize(dh)
    assert hashes["test_of_PythonSerializer"] == hashlib.md5(o).hexdigest()

@pytest.mark.skipif(True, reason = "why does this test compare hashes? What's the intent?")
def test_of_PythonSerializer_enum():
    ps = Serializers.get_serializer()
    enum = data_holder.EnumHolder()
    for x in range(1, 200):
        enum.add_to_list("elem_" + str(x), "val_" + str(x))
    o = ps._serialize_enum({ "test" : enum })
    assert hashes["test_of_PythonSerializer_enum"] == hashlib.md5(o).hexdigest()

@pytest.mark.skipif(True, reason = "why does this test compare hashes? What's the intent?")
def test_of_PythonSerializer_import():
    l = []
    for x in range(20, 400, 3):
        l.append("test_include_" + str(x))
    ps = Serializers.get_serializer()
    o = ps._serialize_include(l)
    assert hashes["test_of_PythonSerializer_import"] == hashlib.md5(o).hexdigest()

def test_of_error_in_SPuschReceiveReq():
    xml = """
         <struct comment="" name="SPuschReceiveReq">
            <member comment="" name="cqiRespDBuffer" type="SPhyDataBuffer"/>
            <member comment="" name="measRespBuffer" type="SPhyDataBuffer"/>
            <member comment="" name="measRespBuffer2" type="SPhyDataBuffer"/>
            <member comment="" name="cellMeasRespBuffer" type="SPhyDataBuffer"/>
            <member comment="" name="rfLoopFlag" type="TBoolean"/>
            <member comment="" name="numOfDelayedUe" rangeDescription="0..MAX_PUSCH_UES_PER_TTI_5MHZ, 0..MAX_PUSCH_UES_PER_TTI_10MHZ, 0..MAX_PUSCH_UES_PER_TTI_15MHZ, 0..MAX_PUSCH_UES_PER_TTI_20MHZ" type="TNumberOfItems"/>
            <member comment="" maxRange="MAX_UINT16" minRange="0" name="delayedUe" type="TCrntiU16">
               <dimension minSize="1" size="MAX_PUSCH_UES_PER_TTI_20MHZ"/>
            </member>
            <member comment="" name="numOfSCellAddressingInfo" rangeDescription="For FSMr3: 0… MAX_NUM_SCELLS; For FSMr2: 0." type="TNumberOfItems"/>
            <member comment="" maxRange="MAX_NUM_OF_PUSCH_RECEIVE_REQ" minRange="0" name="numOfUePuschReq" type="TNumberOfItems"/>
            <member name="uePuschReq" type="SPuschUeReceiveReq">
               <dimension size="THIS_IS_VARIABLE_SIZE_ARRAY"/>
            </member>
         </struct>
"""
    xml_dom_model = minidom.parseString(xml)
    dh = Parser.XMLParser().parsing_xml_files(xml_dom_model)
    ps = Serializers.get_serializer()
    o = ps.serialize(dh)

def test_of_backward_compatibility_serialization():
    xml = ('<struct comment="cmt0" name="SPuschUeReceiveMeasResp">\n'
           '    <member comment="cmt1" maxRange="MAX_UINT16" minRange="0" name="crnti" type="TCrntiU16"/>\n'
           '    <member comment="cmt2" name="ueIndex" type="TUeIndex"/>\n'
           '    <member comment="cmt3" maxRange="EStatusLte_NotOk" minRange="EStatusLte_Ok" name="status" type="EStatusLte"/>\n'
           '    <member comment="cmt4" name="specificCause" type="ESpecificCauseLte"/>\n'
           '    <member comment="cmt5" name="rssi" type="TRssi"/>\n'
           '    <member comment="cmt6" name="interferencePower" type="TInterferencePower"/>\n'
           '    <member comment="cmt7" name="frequencyOffsetPusch" type="TFrequencyOffset"/>\n'
           '    <member comment="cmt8" name="phiReal" type="TTimeEstPhi"/>\n'
           '    <member comment="cmt9" name="phiImag" type="TTimeEstPhi"/>\n'
           '    <member comment="cmt10" maxRange="400" minRange="-200" name="postCombSinr" type="i16"/>\n'
           '    <member comment="cmt11" name="ulCompUsage" rangeDescription="0...1" type="u8"/>\n'
           '    <member comment="cmt12" name="ulReliabilty" type="TBooleanU8"/>\n'
           '    <member comment="cmt13" defaultValue="0" name="subCellId" type="TSubCellIdU8"/>\n'
           '    <member name="explicitPadding1" type="u8"/>\n'
           '    <member name="explicitPadding2" type="u16"/>\n'
           '</struct>')

    xml_dom_model = minidom.parseString(xml)
    dh = Parser.XMLParser().parsing_xml_files(xml_dom_model)
    ps = Serializers.get_serializer()
    output = ps._serialize_msgs(dh.struct_list)

    assert output == ("class SPuschUeReceiveMeasResp(prophy.struct):\n"
                      "    __metaclass__ = prophy.struct_generator\n"
                      "    _descriptor = [('crnti',TCrntiU16), ('ueIndex',TUeIndex), ('status',EStatusLte), ('specificCause',ESpecificCauseLte), ('rssi',TRssi), ('interferencePower',TInterferencePower), ('frequencyOffsetPusch',TFrequencyOffset), ('phiReal',TTimeEstPhi), ('phiImag',TTimeEstPhi), ('postCombSinr',prophy.i16), ('ulCompUsage',prophy.u8), ('ulReliabilty',TBooleanU8), ('subCellId',TSubCellIdU8), ('explicitPadding1',prophy.u8), ('explicitPadding2',prophy.u16)]\n")
