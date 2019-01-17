import sys
import os
import xml.etree.ElementTree as ET

class CommentedTreeBuilder(ET.TreeBuilder):
    def __init__(self, *args, **kwargs):
        super(CommentedTreeBuilder, self).__init__(*args, **kwargs)

    def comment(self, data):
        self.start(ET.Comment, {})
        self.data(data)
        self.end(ET.Comment)

def getProjectFiles(path):
    f_files = []
    for path, subdirs, files in os.walk(path):
        for name in files:
            if name.endswith('.csproj'):
                f_files.append(os.path.join(path, name))
    return f_files

def parseXMLAndUpdate(xmlfile, version):
    namespaces = {'xmlns': 'http://schemas.microsoft.com/developer/msbuild/2003'}
    ET.register_namespace('','http://schemas.microsoft.com/developer/msbuild/2003')
    parser = ET.XMLParser(target=CommentedTreeBuilder())
    tree = ET.parse(xmlfile, parser)
    
    root = tree.getroot()
    
    print(root)
    
    for prop in root.findall('xmlns:PropertyGroup/xmlns:TargetFrameworkVersion', namespaces): 
        prop.text = version
    tree.write(xmlfile, encoding='utf-8', xml_declaration=True);

def targetFrameworkMigrate(path, version):
    files = getProjectFiles(path)
    for f in files:
        parseXMLAndUpdate(f, version)

def main():
    if len(sys.argv) < 2:
        print('invalid arguments')
        print('must provide "-path=<project_dir>" and "-version=<target_framework>" parameters')
        return
    
    params_dict = {}
    for i in range(1, len(sys.argv)):
        key, value = sys.argv[i].split('=')
        params_dict[key] = value
    
    path, version = '', ''
    if '-path' in params_dict.keys():
        path = params_dict['-path']
    else:
        print('path param is not provided')
        return
    
    if '-version' in params_dict.keys():
        version = params_dict['-version']
    else:
        print('version param is not provided')
        return
    
    targetFrameworkMigrate(path, version)
    
if __name__ == '__main__':
    main()
