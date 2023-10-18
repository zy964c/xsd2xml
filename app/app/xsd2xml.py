import click
import xmlschema
import xml.dom.minidom

from xmlschema.validators import (
    XsdElement,
    XsdAnyElement,
    XsdComplexType,
    XsdAtomicBuiltin,
    XsdSimpleType,
    XsdList,
    XsdUnion,
)


# sample data is hardcoded
def valsmap(v):
    # numeric types
    v["decimal"] = "-3.72"
    v["float"] = "-42.217E11"
    v["double"] = "+24.3e-3"
    v["integer"] = "-176"
    v["positiveInteger"] = "+3"
    v["negativeInteger"] = "-7"
    v["nonPositiveInteger"] = "-34"
    v["nonNegativeInteger"] = "35"
    v["long"] = "567"
    v["int"] = "109"
    v["short"] = "4"
    v["byte"] = "2"
    v["unsignedLong"] = "94"
    v["unsignedInt"] = "96"
    v["unsignedShort"] = "24"
    v["unsignedByte"] = "17"
    # time/duration types
    v["dateTime"] = "2004-04-12T13:20:00-05:00"
    v["date"] = "2004-04-12"
    v["gYearMonth"] = "2004-04"
    v["gYear"] = "2004"
    v["duration"] = "P2Y6M5DT12H35M30S"
    v["dayTimeDuration"] = "P1DT2H"
    v["yearMonthDuration"] = "P2Y6M"
    v["gMonthDay"] = "--04-12"
    v["gDay"] = "---02"
    v["gMonth"] = "--04"
    # string types
    v["string"] = "txt"
    v["normalizedString"] = "normalizedString"
    v["token"] = "token"
    v["language"] = "en-US"
    v["NMTOKEN"] = "A_BCD"
    v["NMTOKENS"] = "ABCD 123"
    v["Name"] = "myElement"
    v["NCName"] = "_my.Element"
    # magic types
    v["ID"] = "IdID"
    v["IDREFS"] = "IDrefs"
    v["ENTITY"] = "prod557"
    v["ENTITIES"] = "prod557 prod563"
    # oldball types
    v["QName"] = "pre:myElement"
    v["boolean"] = "true"
    v["hexBinary"] = "0FB8"
    v["base64Binary"] = "0fb8"
    v["anyURI"] = "http://some.web.site.ru"
    v["notation"] = "asd"


class GenXML:
    def __init__(self, xsd, elem, enable_choice, verbose, recursion_depth):
        self.xsd = xmlschema.XMLSchema(xsd)
        self.elem = elem
        self.enable_choice = enable_choice
        self.root = True
        self.vals = {}
        self.rec = 0
        self.rec_limit = int(recursion_depth)
        self.verbose = verbose
        self.resulting_xml = []

    # shorten the namespace
    def short_ns(self, ns):
        for k, v in self.xsd.namespaces.items():
            if k == "":
                continue
            if v == ns:
                return f"{k}:"
        return ""

    def output(self, data: str) -> None:
        if data.startswith("<!--") and not self.verbose:
            return
        self.resulting_xml.append(data)

    # if name is using long namespace,
    # lets replace it with the short one
    def use_short_ns(self, name):
        if name[0] == "{":
            x = name.find("}")
            ns = name[1:x]
            return self.short_ns(ns) + name[x + 1 :]
        return name

    # remove the namespace in name
    def remove_ns(self, name):
        if name[0] == "{":
            x = name.find("}")
            return name[x + 1 :]
        return name

    # header of xml doc
    def print_header(self):
        self.output('<?xml version="1.0" encoding="UTF-8" ?>')

    # put all defined namespaces as a string
    def ns_map_str(self):
        ns_all = ""
        for k, v in self.xsd.namespaces.items():
            if k == "":
                continue
            else:
                ns_all += "xmlns:" + k + '="' + v + '"' + " "
        return ns_all

    # start a tag with name
    def start_tag(self, name, attributes=None):
        x = "<" + name
        if self.root:
            self.root = False
            x += " " + self.ns_map_str()
        if attributes:
            for attr_name, attr_obj in attributes.items():
                if attr_name:
                    try:
                        attr_type = attr_obj.type.id
                    except Exception as ex:
                        attr_type = "string"
                    if not attr_type:
                        attr_type = "string"
                    x += f' {self.remove_ns(attr_name)}="{self.genval(attr_type)}"'
        x += ">"
        return x

    # end a tag with name
    def end_tag(self, name):
        return "</" + name + ">"

    # make a sample data for primitive types
    def genval(self, name):
        name = self.remove_ns(name)
        if name in self.vals:
            return self.vals[name]
        return "ERROR !"

    # print a group
    def group2xml(self, g):
        try:
            model = str(g.model)
        except Exception as ex:
            self.output("<!--empty-->")
            return
        model = self.remove_ns(model)
        try:
            nextg = g._group
        except Exception as ex:
            self.output("<!--empty-->")
            return
        y = len(nextg)
        if y == 0:
            self.output("<!--empty-->")
            return

        self.output("<!--START:[" + model + "]-->")
        if self.enable_choice and model == "choice":
            self.output(
                "<!--next item is from a [choice] group with size=" + str(y) + "-->"
            )
        else:
            self.output(
                "<!--next " + str(y) + " items are in a [" + model + "] group-->"
            )

        for ng in nextg:
            if isinstance(ng, XsdElement):
                self.node2xml(ng)
            elif isinstance(ng, XsdAnyElement):
                self.node2xml(ng)
            else:
                self.group2xml(ng)

            if self.enable_choice and model == "choice":
                break
        self.output("<!--END:[" + model + "]-->")

    # print a node
    def node2xml(self, node):
        self.rec += 1
        if node.min_occurs == 0:
            self.output("<!--next 1 item is optional (minOcuurs = 0)-->")
        if not node.max_occurs:
            node.max_occurs = 0
        if node.max_occurs > 1:
            self.output("<!--next 1 item is multiple (maxOccurs > 1)-->")

        if isinstance(node, XsdAnyElement):
            self.rec -= 1
            return

        if isinstance(node.type, XsdComplexType):
            n = self.use_short_ns(node.name)
            if node.type.is_simple():
                self.output("<!--simple content-->")
                try:
                    tp = str(node.type.content_type.id)
                except Exception as ex:
                    tp = " "
                self.output(
                    self.start_tag(n, node.attributes)
                    + self.genval(tp)
                    + self.end_tag(n)
                )
            else:
                self.output("<!--complex content-->")
                self.output(self.start_tag(n, node.attributes))
                if self.rec_limit > self.rec:
                    self.group2xml(node.type.content)
                self.output(self.end_tag(n))
        elif isinstance(node.type, XsdAtomicBuiltin):
            n = self.use_short_ns(node.name)
            tp = str(node.type.id)
            self.output(
                self.start_tag(n, node.attributes) + self.genval(tp) + self.end_tag(n)
            )
        elif isinstance(node.type, XsdSimpleType):
            n = self.use_short_ns(node.name)
            if isinstance(node.type, XsdList):
                self.output("<!--simpletype: list-->")
                tp = str(node.type.item_type.id)
                self.output(
                    self.start_tag(n, node.attributes)
                    + self.genval(tp)
                    + self.end_tag(n)
                )
            elif isinstance(node.type, XsdUnion):
                self.output("<!--simpletype: union.-->")
                self.output("<!--default: using the 1st type-->")
                tp = str(node.type.member_types[0].id)
                self.output(
                    self.start_tag(n, node.attributes)
                    + self.genval(tp)
                    + self.end_tag(n)
                )
            else:
                tp = str(node.type.base_type.id)
                self.output(
                    self.start_tag(n, node.attributes)
                    + self.genval(tp)
                    + self.end_tag(n)
                )
        else:
            self.output("ERROR: unknown type: " + node.type)
        self.rec -= 1

    def to_stdout(self):
        xml_str = "\n".join(self.resulting_xml)
        dom = xml.dom.minidom.parseString(xml_str)
        print(dom.toprettyxml(newl=""))

    # setup and print everything
    def run(self):
        valsmap(self.vals)
        self.print_header()
        self.node2xml(self.xsd.elements[self.elem])
        self.to_stdout()


@click.command()
@click.option(
    "-s",
    "--schema",
    required=True,
    type=click.Path(exists=True, file_okay=True, resolve_path=True),
    help="Путь к xsd схеме",
)
@click.option(
    "-t",
    "--root-tag",
    required=True,
    type=click.STRING,
    help="Корневой элемент xml",
)
@click.option(
    "-c",
    "--choice",
    default=False,
    is_flag=True,
    help="Создавать только первый вариант choice",
    show_default=True,
)
@click.option(
    "-v",
    "--verbose",
    default=False,
    is_flag=True,
    help="Включить в вывод комментарии",
    show_default=True,
)
@click.option(
    "-r",
    "--recursion-depth",
    default=8,
    type=click.INT,
    help="Максимальная глубина рекурсии",
    show_default=True,
)
def cli(schema, root_tag, choice, verbose, recursion_depth) -> None:
    generator = GenXML(schema, root_tag, choice, verbose, recursion_depth)
    generator.run()


if __name__ == "__main__":
    cli()
