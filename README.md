# Python CDK - Security Group

Deploy Security Groups to Multi Accounts using StackSets.
Change management is done centrally.

Example.

vars/

sg-xxxxxxxxxx.py

class securitygroup():
## Defaul-Web    
    def default_web_ingress():
        Rule1 = ['tcp', 443, 443, '172.16.112.0/24']
        Rule2 = ['tcp', 80, 80, '172.16.112.0/24']

        return [Rule1, Rule2]

    def default_web_egress():
        Rule1 = ['tcp', 80, 80, '10.10.1.1/24']
        
        return [Rule1]
## Defaul-Web - End

## Default-DB
    def default_db_ingress():
        Rule1 = ['tcp', 443, 443, '0.0.0.0/0']
        Rule2 = ['tcp', 80, 80, '0.0.0.0/0']

        return [Rule1, Rule2]

    def default_db_egress():
        Rule1 = ['tcp', 80, 80, '0.0.0.0/0']
        
        return [Rule1]
## Default-DB-End

....
..


