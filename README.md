![](http://miaozn.github.io/misc/img/xsd2xml.png)     
# xsd2xml
This is a simple python script to help you generate some xmls if you have a xsd. It uses the [xmlschema](https://github.com/brunato/xmlschema) library to parse the given schema document and then populate some hardcoded values. check the following example. 

# Install
```bash
$ pip install xsd2xml-0.0.1-py3-none-any.whl
```

## XSD
```xsd
<?xml version="1.0" encoding="utf-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="root" type="root"/>
  <xs:complexType name="root">
    <xs:choice>
      <xs:sequence>
        <xs:element name="empno" type="xs:string"/>
        <xs:element name="designation" type="xs:string"/>
      </xs:sequence>
      <xs:sequence>
        <xs:element name="name" type="xs:string"/>
        <xs:element name="age" type="xs:unsignedByte"/>
      </xs:sequence>
      <xs:element name="sku" type="SKU"/>
      <xs:element name="ppk" type="xs:integer"/>
      <xs:element name="alo" type="xs:date"/>
      <xs:any minOccurs="0"/>
      <xs:element name="shoesize">
        <xs:complexType>
          <xs:simpleContent>
            <xs:extension base="xs:integer">
              <xs:attribute name="country" type="xs:string"/>
            </xs:extension>
          </xs:simpleContent>
        </xs:complexType>
      </xs:element>
      <xs:element name="jeans_size">
        <xs:simpleType>
          <xs:union memberTypes="sizebyno sizebystring"/>
        </xs:simpleType>
      </xs:element>
      <xs:element name="intvalues" type="valuelist"/>
    </xs:choice>
  </xs:complexType>
  <xs:simpleType name="SKU">
    <xs:restriction base="xs:string">
      <xs:pattern value="\d{3}\w{3}"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:simpleType name="sizebyno">
    <xs:restriction base="xs:positiveInteger">
      <xs:maxInclusive value="42"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:simpleType name="sizebystring">
    <xs:restriction base="xs:string">
      <xs:enumeration value="small"/>
      <xs:enumeration value="medium"/>
      <xs:enumeration value="large"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:simpleType name="valuelist">
    <xs:list itemType="xs:integer"/>
  </xs:simpleType>
</xs:schema>
```
## XML
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!--complex content-->
<root xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <!--START:[choice]-->
  <!--next 9 items are in a [choice] group-->
  <!--START:[sequence]-->
  <!--next 2 items are in a [sequence] group-->
  <empno>lol</empno>
  <designation>lol</designation>
  <!--END:[sequence]-->
  <!--START:[sequence]-->
  <!--next 2 items are in a [sequence] group-->
  <name>lol</name>
  <age>17</age>
  <!--END:[sequence]-->
  <sku>lol</sku>
  <ppk>-176</ppk>
  <alo>2004-04-12</alo>
  <!--next 1 item is optional (minOcuurs = 0)-->
  <_ANY_/>
  <!--simple content-->
  <shoesize>-176</shoesize>
  <!--simpletype: union.-->
  <!--default: using the 1st type-->
  <jeans_size>+3</jeans_size>
  <!--simpletype: list-->
  <intvalues>-176</intvalues>
  <!--END:[choice]-->
</root>
```
The command to get the above xml:  
```bash
$ xsd2xml -s 1.xsd -t root
```
## Usage
```bash
$ xsd2xml --help

Usage: xsd2xml [OPTIONS]

Options:
  -s, --schema PATH              Путь к xsd схеме  [required]
  -t, --root-tag TEXT            Корневой элемент xml  [required]
  -c, --choice                   Создавать только первый вариант choice
  -v, --verbose                  Включить в вывод комментарии
  -r, --recursion-depth INTEGER  Максимальная глубина рекурсии  [default: 8]
  --help                         Show this message and exit.
```
## Handle `<choice>`
You can generate all in a choice group (as the above example shows) or you can generate the 1st element in the choice group by the "-c" option.
### command
```bash
$ xsd2xml -s 1.xsd -t root -c
```
### xml
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!--complex content-->
<root xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <!--START:[choice]-->
  <!--next item is from a [choice] group with size=9-->
  <!--START:[sequence]-->
  <!--next 2 items are in a [sequence] group-->
  <empno>lol</empno>
  <designation>lol</designation>
  <!--END:[sequence]-->
  <!--END:[choice]-->
</root>
```
