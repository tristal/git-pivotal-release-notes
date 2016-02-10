import sys
import github
import requests
import re

class PivotalProject(object):
    id = ""
    name = ""

    def __init__(self, id, name):
        self.id = id
        self.name = name

class PivotalStory(object):
    id = ""
    name = ""
    projectName = ""

    def __init__(self, id, name, projectName):
        self.id = id
        self.name = name
        self.projectName = projectName

    def printString(pivotalStory):
        print "\t{0} [#{1}] {2}".format(pivotalStory.projectName, pivotalStory.id, pivotalStory.name.encode("utf-8"))

def getPivotalStorySortKey(pivotalStory):
        return pivotalStory.projectName + pivotalStory.id

def usage():
    if len(sys.argv) != 7:
        print "usage: python git-pivotal-release-notes.py <githubKey> <pivotalKey> <gitRepositoryName> <gitFromBranch> <gitToBranch> <pivotalCommaSeparatedProjectIds>"
        sys.exit()

def find_repo(repo_list, name):
    for repo in repo_list:
        if repo.name == name:
            return repo

def get_pivotal_projects(token, pivotalProjectIds):
    split = pivotalProjectIds.split(',')
    results = []
    for pivotalProjectId in split:
        response = requests.get("https://www.pivotaltracker.com/services/v5/projects/{0}".format(pivotalProjectId), headers={'X-TrackerToken': token})
        responseJson = response.json()
        if "name" in responseJson:
            results.append(PivotalProject(pivotalProjectId, responseJson["name"]))
    return results

def compare_branches_and_build_stories(repo, toBranch, fromBranch, pivotalKey, pivotalProjects):
    compare = repo.compare(toBranch, fromBranch)

    print "\tcomparing {0} to {1} -- total commits: {2}".format(fromBranch, toBranch, str(compare.total_commits))
    print "\tretrieving commits and story information..."

    featureIds = set()
    results = []
    for gitCommit in compare.commits:
        featureId = parse_commit(gitCommit.commit.message)
        if featureId is not None:
            if featureId in featureIds:
                continue
            else:
                featureIds.add(featureId) # track unique stories
                pivotalStory = get_feature_name(pivotalKey, pivotalProjects, featureId)
                if pivotalStory is not None:
                    results.append(pivotalStory)

    return results

def parse_commit(body):
    match = re.match(r'^\[#(.*)\]', body, 0)
    if match:
        return match.group(1)
    else:
        match = re.match(r'^\[Finishes #(.*)\]', body, 0)
        if match:
            return match.group(1)
        else:
            return None

def get_feature_name(token, pivotalProjects, storyId):
    for pivotalProject in pivotalProjects:
        response = requests.get("https://www.pivotaltracker.com/services/v5/projects/{0}/stories/{1}".format(pivotalProject.id, storyId), headers={'X-TrackerToken': token})
        responseJson = response.json()
        if "name" in responseJson:
            return PivotalStory(storyId, responseJson["name"], pivotalProject.name)

def main():
    usage();

    githubKey = sys.argv[1]
    pivotalKey = sys.argv[2]
    repository = sys.argv[3]
    fromBranch = sys.argv[4]
    toBranch = sys.argv[5]
    pivotalProjectIds = sys.argv[6]

    print "config:"
    print "\trepository: " + repository
    print "\tfromBranch: " + fromBranch
    print "\ttoBranch: " + toBranch
    print "\tpivotalProjectIds: " + pivotalProjectIds

    g = github.Github(githubKey)

    ### GITHUB
    repos = g.get_user().get_repos()
    repo = find_repo(repos, repository)

    ### PIVOTAL
    pivotalProjects = get_pivotal_projects(pivotalKey, pivotalProjectIds)

    ### DO THE WORK
    print "running..."
    results = compare_branches_and_build_stories(repo, toBranch, fromBranch, pivotalKey, pivotalProjects)

    print "results:"
    print ""
    print "I've just completed a {0} release for {1}. Here is a list of stories that were included:".format(toBranch, repository)
    for result in sorted(results, key=getPivotalStorySortKey):
        result.printString()
    print ""

if __name__ == "__main__":
    main()
