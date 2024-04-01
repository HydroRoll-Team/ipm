from typing import List
from ipm.models.index import Yggdrasil
from ipm.models.ipk import InfiniProject
from ipm.models.requirement import Requirement


def get_requirements(
    requirement: Requirement, resolved: List[str] = []
) -> List[Requirement]:
    requirements = {}
    for req in requirement.yggdrasil.get_requirements(requirement.name):
        if req.name in resolved:
            continue
        resolved.append(req.name)
        requirements[req.name] = req
        sub_reqs = get_requirements(req, resolved)
        for sub_seq in sub_reqs:
            requirements[sub_seq.name] = sub_seq

    return list(requirements.values())


def get_requirements_by_project(project: InfiniProject) -> List[Requirement]:
    requirements = {}
    for requirement in project.requirements:
        requirements[requirement.name] = requirement
        reqs = get_requirements(requirement)
        for req in reqs:
            requirements[req.name] = req
    return list(requirements.values())
