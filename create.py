import xml.etree.cElementTree as et
import uuid

def make_config(name, disk_path, ram, vcpu):
    domain = et.Element("domain")

    namexml = et.SubElement(domain, "name")
    name.text = name

    uuidxml = et.SubElement(domain, "uuid")
    uuidxml.text = uuid.uuid1()

    memoryxml = et.SubElement(domain, "memory")
    memoryxml.set("unit", "MB")
    memoryxml.text = ram

    cmemoryxml = et.SubElement(domain, "currentMemory")
    cmemoryxml.set("unit", "MB")
    cmemoryxml.text = ram

    vcpuxml = et.SubElement(domain, "vcpu")
    vcpuxml.set("placement", "static")
    vcpuxml.text = vcpu

    osxml = et.SubElement(domain, "os")
    
    typexml = et.SubElement(osxml, "type")
    typexml.set("arch", "x86_64")
