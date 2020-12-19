import importlib

def load_module_func(module_name):
    tmp = importlib.import_module(module_name)
    return tmp

#print(load_module_func("vars.sg-247338496055"))

test = load_module_func("vars.sg-247338496055")

#print(class_list)
sg = test.securitygroup

print(sg.default_web('egress'))

#print(dir(test))

