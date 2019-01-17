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

def parseXMLAndUpdate(xmlfile, mapping_dict):
    hintPathTag = 'xmlns:HintPath'
    referenceTag = 'xmlns:ItemGroup/xmlns:Reference'
    namespaces = {'xmlns': 'http://schemas.microsoft.com/developer/msbuild/2003'}
    ET.register_namespace('','http://schemas.microsoft.com/developer/msbuild/2003')
    parser = ET.XMLParser(target=CommentedTreeBuilder())
    tree = ET.parse(xmlfile, parser)
    
    root = tree.getroot()
    
    for prop in root.findall(referenceTag, namespaces):
        for old_val in [key for key, value in mapping_dict.items() if prop.attrib['Include'] == key or key+',' in prop.attrib['Include']]:
            new_val = mapping_dict[old_val]
            prop.attrib['Include'] = new_val
            if prop.find(hintPathTag, namespaces) != None:
                prop.find(hintPathTag, namespaces).text = prop.find(hintPathTag, namespaces).text.replace(old_val, new_val)
    tree.write(xmlfile, encoding='utf-8', xml_declaration=True);

def referencesUpdator(path, mapping_dict):
    files = getProjectFiles(path)
    for f in files:
        parseXMLAndUpdate(f, mapping_dict)

def main():
    if len(sys.argv) < 2:
        print('invalid arguments')
        print('must contain atleast one mapping in the form of <existing_assembly>=<updated_assembly> separated by space(if multiple)')
        return
    params_dict = {}
    mapping_dict = {}
    for i in range(1, len(sys.argv)):
        key, value = sys.argv[i].split('=')
        params_dict[key] = value
    
    path, version = '', ''
    if '-path' in params_dict.keys():
        path = params_dict['-path']
    else:
        print('path param is not provided')
        return
    
    try:
        for i in range(2, len(sys.argv)):
            arg_split = sys.argv[i].split('=')
            mapping_dict[arg_split[0]] = arg_split[1]
    except:
        print('error in mappings format, please check and try again')
        
    
    referencesUpdator(path, mapping_dict)
    print('Done! References Updated!')
    
if __name__ == '__main__':
    main()
