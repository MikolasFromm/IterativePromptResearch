from typing import List
from data_sources.worldBank_node import WorldBankNode
from instances.node import select_subsection_operation, open_table_operation
import xml.etree.ElementTree as ET

worldbank_namespaces =  {
        'nt': 'urn:eu.europa.ec.eurostat.navtree'
    }

class Table:
    def __init__(self, name : str):
        self.name = name
    
    def __str__(self) -> str:
        return f"Table: {self.name}"
    
    def __repr__(self) -> str:
        return self.__str__()

class DataSet:
    def __init__(self, name : str):
        self.name = name
        self.children: List['DataSet' | 'Table'] = []

    def isleaf(self):
        return len(self.children) == 0
    
    def __str__(self) -> str:
        return f"DataSet: {self.name}"
    
    def __repr__(self) -> str:
        return self.__str__()

class WorldBank():
    def __init__(self):
        """Initializes the WorldBank data source. Loads the whole table of contents."""
        self.dataSet = self.__parse_xml_tree('data_sources/worldBank/table_of_contents.xml')

    def __parse_xml_tree(self, path : str):
        """Parses the xml tree from the given path and returns the root node."""
        tree = ET.parse(path)
        root = tree.getroot()

        dataset : DataSet = DataSet("WorldBank")
        dataset.children = self.__parse_root(root)

        return dataset
    
    def __parse_root(self, root : ET.Element) -> List['DataSet']:
        """Parses the given root node and returns the corresponding DataSet object."""
        datasets = []
        for branch in root.findall('nt:branch', worldbank_namespaces):
            title = branch.find('nt:title/[@language="en"]', worldbank_namespaces).text

            branch_dataset = DataSet(title)

            for child in branch.findall('nt:children', worldbank_namespaces):
                branch_dataset.children = self.__parse_root(child)

            datasets.append(branch_dataset)

        for leaf in root.findall('nt:leaf', worldbank_namespaces):
            title = leaf.find('nt:title/[@language="en"]', worldbank_namespaces).text

            datasets.append(Table(title))

        return datasets
    
    def transformToNode(self) -> WorldBankNode:
        """Transforms the whole WorldBank data source into a WorldBankNode object."""
        return self.__transformDataSet(self.dataSet, 0)
    
    def __transformDataSet(self, dataset : DataSet, depth : int) -> WorldBankNode:
        """Transforms the given DataSet object into a WorldBankNode object."""
        node = WorldBankNode(select_subsection_operation, depth, dataset.name)
        for child in dataset.children:
            if (child.isleaf()):
                node.children.append(WorldBankNode(open_table_operation, depth + 1, child.name))
            else:
                node.children.append(self.__transformDataSet(child, depth + 1))
                
        return node