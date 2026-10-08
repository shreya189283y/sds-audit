import re 

def is_valid_cas(cas):
    new_cas = cas.replace("-", "")
    cascheck = int(new_cas[-1])
    new_cas = new_cas[:-1]
    new_cas = reversed(new_cas)
    total=0
    for index, i in enumerate(new_cas,1):
        total += (index)* int(i)
    return total % 10 == cascheck

def find_cas(text):
    failed_cas_list = []
    cas_list = re.findall(r"\b\d{2,7}-\d{2}-\d\b", text)
    for i in cas_list:
        if not is_valid_cas(i):
            cas_list.remove(i)
            failed_cas_list.append(i)
    return cas_list, failed_cas_list
