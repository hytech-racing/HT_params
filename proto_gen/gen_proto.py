import json

def format_default_value(value, param_type):
    if param_type == 'bool':
        return 'true' if value else 'false'
    return str(value)

def verify_parameters(parameters):
    allowed_types = {'float', 'bool', 'int'}
    names_seen = set()

    for param in parameters:
        param_type = param['type']
        param_name = param['name']
        default_value = param['defaultValue']

        if param_name in names_seen:
            raise ValueError(f"Duplicate parameter name detected: {param_name}")
        names_seen.add(param_name)

        if param_type not in allowed_types:
            raise ValueError(f"Unsupported type '{param_type}' for parameter '{param_name}'. Allowed types are: {', '.join(allowed_types)}")
        
        if param_type == 'int' and not isinstance(default_value, int):
            raise ValueError(f"Default value for {param_name} must be an int")
        elif param_type == 'float' and not isinstance(default_value, (float, int)):
            raise ValueError(f"Default value for {param_name} must be a float")
        elif param_type == 'bool' and not isinstance(default_value, bool):
            raise ValueError(f"Default value for {param_name} must be a bool")

def generate_proto(parameters, msgs_file='msgs.proto', output_file='ht_eth.proto'):
    proto_types = {
        'int': 'int32',
        'float': 'float',
        'bool': 'bool'
    }
    message_names = []

    # Read existing messages from msgs.proto
    with open(msgs_file, 'r') as file:
        msgs_content = file.read()

    # Generate content for config.proto
    config_content = "message config {\n"
    field_number = 1  # Start field numbers at 1
    for param in parameters:
        param_name = param['name']
        param_type = param['type']
        default_value = format_default_value(param['defaultValue'], param_type)
        proto_type = proto_types[param_type]
        config_content += f"    {proto_type} {param_name} = {field_number};\n"
        field_number += 1
    config_content += "}\n"

    # Combine msgs_content with config_content
    combined_content = msgs_content + "\n" + config_content

    # Extract message names for the union type
    for line in combined_content.splitlines():
        if line.strip().startswith('message'):
            message_name = line.strip().split()[1]
            if message_name != "HT_ETH_Union":  # Exclude the union message itself
                message_names.append(message_name)

    # Create union message using oneof
    union_message = "message HT_ETH_Union {\n  oneof type_union {\n"
    for i, name in enumerate(message_names, start=1):
        msg_name = name + "_"
        union_message += f"    {name} {msg_name.lower()} = {i};\n"
    union_message += "  }\n}\n"

    # Write to output file
    with open(output_file, 'w') as file:
        file.write(combined_content + "\n" + union_message)

if __name__ == "__main__":
    with open("parameters.json", "r") as file:
        params = json.load(file)
    verify_parameters(params)
    generate_proto(params)
