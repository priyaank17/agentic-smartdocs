"""This file contains the functions to extract the id from the control narrative data"""


def add_narrative_id(result, id_number):
    """This function adds the narrative id to the result object"""
    narrative_id = "narrative_" + str(id_number)
    for connection in result:
        connection["narrative_id"] = narrative_id


def flatten(results):
    """This function flattens the list of list"""
    results = [item for sublist in results for item in sublist]
    return results


def add_id(control, results):
    """This function adds the id to the result object"""
    i = 0
    for connection in results:
        new_id = control + str(i + 1)
        i = i + 1
        connection[f"{control}id"] = new_id
