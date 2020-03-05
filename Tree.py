import warnings
import numpy as np

class Tree():

    def __init__(self, nodes: dict):
        """
        Inits the tree class

        @params
        :nodes: dict of {node: root} relations to be used
        """
        self.__visited_nodes = set()
        self._nodes = nodes

        self.__callers = []
        self.__roots = []
        self.__levels = []

        return


    def tree(self):
        """
        Returns tree interable as touple  
        (node, root, level)
        Can be used further to create data frame or list
        """
        if len(self.__callers) == 0:
            raise ValueError("Tree empty or not searched yet.")
        return zip(self.__callers, self.__roots, self.__levels)


    def search(self):
        """
        Searches and generates the tree relation resulting all posible 
        root-node relations given as (node, root) with it's depth
        
        Example:
        (A, B); (B, C)
        
        Result:
        node | root | level
        A | A | 0
        B | B | 0
        B | A | 1
        C | C | 0
        C | B | 1
        C | A | 2
        """

        # re-initalize the tree
        self.__callers = []
        self.__roots = []
        self.__levels = []

        i = 0  # step
        n = len(self._nodes)  # nodes to be searched
        
        # loop through nodes and find all possible relations
        for node in self._nodes:
            try:
                self._search_root(node, node)  # search root for a given node
            except RecursionError:
                raise RecursionError("Recursion error occured in node: {}".format(node))
            
            i += 1
            self.__visited_nodes.clear()  # clear list of the visited nodes
            if (i % 1000 == 0):
                print ("Progress: {}".format(round(i/n * 100, 2)))
        
        print("Progress: 100.00")
        return


    def _search_root(self, node_init: str, node: str, level=0):
        """
        Recursivelly searches the top root of the node.
        If node has no roots it is assumed that it is in only reflexive relation

        In case of cycle execution is terminated
        """
        try:
            next_node = self._nodes[node]  # take next node to be search
        except KeyError:  # if there is no paren available, skip
            msg = "Unresolved reference from node {} to it's root {}"
            warnings.warn(msg.format(node_init, node), RuntimeWarning)
            return

        # check for the cycle in the relation
        if node in self.__visited_nodes:  
            msg = "Cycle occured between nodes: {}, {}"
            msg += "\n(Caller: {})"
            warnings.warn(msg.format(node, next_node, node_init), RuntimeWarning)
            return 

        # Add new record to the set
        self.__callers.append(node_init)
        self.__roots.append(node)
        self.__levels.append(level)

        # check if the requested node is not the final root
        if next_node != next_node:  
            return 

        self.__visited_nodes.add(node)  # add to the list of visited nodes
        self._search_root(node_init, next_node, level+1)  # continue search  

        return

    def prune(self):
        """
        Removes all partial relations between top root and it's nodes leaving
        only one that groups them all

        Example:
        (A, B); (B, C)
        
        Tree relation:
        node | root | level
        A | A | 0
        B | B | 0
        B | A | 1
        C | C | 0
        C | B | 1
        C | A | 2

        Result: (Tree after prune)
        node | root | level
        A | A | 0
        B | A | 1
        C | A | 2
        """

        # Check if tree has been searched or is not empty
        if (len(self.__callers) == 0):
            raise UnboundLocalError("Tree empty nothing to prune.")

        # Transform relevant variables into numpy arrays
        levels = np.array(self.__levels)
        is_root = np.where(levels==0, True, False)  # determine all possible roots
        
        _roots = np.array(self.__roots)  # initial array of the roots
        _nodes = np.array(self.__callers)  # initial array of the nodes

        # Select all roots (can include node-roots)
        roots = _roots[is_root]
        roots = set(roots)

        # Select all nodes (can include node-roots)
        nodes = _nodes[~is_root]

        # The trick is that final root does not have any upper root
        # except itself thus we have now to remove all nodes 
        # that are also roots (exists in both sets of roots and nodes)
        master_roots = roots - set(nodes)
        master_roots = np.array(list(master_roots))
        
        # Search for all children of the master root
        idx = np.isin(_roots, master_roots)  # select only master root nodes

        self.__callers = np.array(self.__callers)[idx]
        self.__roots = _roots[idx]
        self.__levels = levels[idx]

        return 
