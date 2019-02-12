import pkg_resources
installed_packages = [d for d in pkg_resources.working_set]
print(installed_packages)
