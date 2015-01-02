import xml.etree.cElementTree as et
import uuid

def make_config(name, disk_path, ram, vcpu):
    domain = et.Element("domain")

    namexml = et.SubElement(domain, "name")
    namexml.text = name

    uuidxml = et.SubElement(domain, "uuid")
    uuidxml.text = str(uuid.uuid1())

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
    typexml.text = "hvm"

    bootdev1xml = et.SubElement(osxml, "boot")
    bootdev1xml.set("dev", "hd")

    featurexml = et.SubElement(domain, "features")
    acpixml = et.SubElement(featurexml, "acpi")
    apicxml = et.SubElement(featurexml, "apic")
    paexml = et.SubElement(featurexml, "pae")

    clockxml = et.SubElement(domain, "clock")
    clockxml.set("offset", "utc")

    onpoweroffxml = et.SubElement(domain, "on_poweroff")
    onpoweroffxml.text = "destroy"

    onrebootxml = et.SubElement(domain, "on_reboot")
    onrebootxml.text = "restart"

    oncrashxml = et.SubElement(domain, "on_crash")
    oncrashxml.text = "restart"

    tree = et.ElementTree(domain)
    path = "/var/configs/vm%s.xml" % str(name)
    tree.write(path)
