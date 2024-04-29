import json
import hashlib

def generate_identifier(name):
    """ Create a hash of the parameter name and return the first 8 characters. """
    hash_obj = hashlib.sha256(name.encode())
    return hash_obj.hexdigest()[:8]

def format_default_value(value, param_type):
    print(value)
    if param_type == 'bool':
        return 'true' if value else 'false'
    return value

def verify_parameters(parameters):
    allowed_types = {'float', 'bool', 'int'}
    names_seen = set()

    for param in parameters:
        param_type = param['type']
        param_name = param['name']
        default_value = param['defaultValue']

        
        # Check for duplicate names
        if param_name in names_seen:
            raise ValueError(f"Duplicate parameter name detected: {param_name}")
        names_seen.add(param_name)

        # Check for allowed types
        if param_type not in allowed_types:
            raise ValueError(f"Unsupported type '{param_type}' for parameter '{param_name}'. Allowed types are: {', '.join(allowed_types)}")
        # Check if the default value matches the type
        if param_type == 'int' and not type(default_value) is int:
            raise ValueError(f"Default value for {param_name} must be an int")
        elif param_type == 'float' and not type(default_value) in [float, int]:  # Allow ints as they are implicitly convertible to floats in C++
            raise ValueError(f"Default value for {param_name} must be a float")
        elif param_type == 'bool' and not type(default_value) is bool:
            raise ValueError(f"Default value for {param_name} must be a bool")

def generate_code(parameters):
    identifiers = {}
    type_bases = {}
    
    with open("Parameters.h", "w") as f:
        f.write("#pragma once\n")
        f.write("#include <unordered_map>\n\n")
        f.write("namespace Parameters {\n\n")

        for param in parameters:
            param_type = param['type']
            if param_type not in type_bases:
                type_bases[param_type] = []
                # Define base classes for each type
                f.write(f"class {param_type.capitalize()}Parameter {{\n")
                f.write("public:\n")
                f.write(f"    virtual {param_type} get() const = 0;\n")
                f.write(f"    virtual void set({param_type} value) = 0;\n")
                f.write("    virtual ~" + param_type.capitalize() + "Parameter() {}\n")
                f.write("};\n\n")
        
        for param in parameters:
            param_name = param['name']
            param_type = param['type']
            default_value = format_default_value(param['defaultValue'], param_type)
            identifier = generate_identifier(param_name)
            identifiers[identifier] = {'name': param_name, 'type': param_type}
            type_bases[param_type].append((identifier, param_name, default_value))

            # Define parameter-specific classes
            f.write(f"class {param_name} : public {param_type.capitalize()}Parameter {{\n")
            f.write(f"    {param_type} value;\n")
            f.write("public:\n")
            f.write(f"    {param_name}() : value({default_value}) {{}}\n")
            f.write(f"    {param_type} get() const override {{ return value; }}\n")
            f.write(f"    void set({param_type} v) override {{ value = v; }}\n")
            f.write("};\n\n")
        

        for type_name, instances in type_bases.items():
            for identifier, param_name, _ in instances:
                f.write(f"{param_name} {param_name}Instance;\n")
            f.write(f"std::unordered_map<const char *, Parameters::{type_name.capitalize()}Parameter*> {type_name}LookupMap = {{\n")
            for identifier, param_name, _ in instances:
                f.write(f"    {{\"{identifier}\", &{param_name}Instance}},\n")
            f.write("};\n\n")

        f.write("}\n\n")  # Close the namespace
    # Save identifiers to JSON
    with open("identifiers.json", "w") as jf:
        json.dump(identifiers, jf, indent=4)

if __name__ == "__main__":
    with open("parameters.json", "r") as file:
        params = json.load(file)
    verify_parameters(params)
    generate_code(params)
