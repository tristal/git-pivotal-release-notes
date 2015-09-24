Script to generate a simple release text listing git commits linked to pivotal stories (apologies for the hacky script, first time writing Python).

Requires:
 - Github API gem ([PyGithub](https://pypi.python.org/pypi/PyGithub));
 - Github API key (https://github.com/settings/tokens);
 - Pivotal API key (https://www.pivotaltracker.com/profile);

Usage:

`python git-pivotal-release-notes.py <githubKey> <pivotalKey> <gitRepositoryName> <gitFromBranch> <gitToBranch> <pivotalCommaSeparatedProjectIds>"`

Example output:

```
I've just completed a **GithubDestinationBranchName** release for **GithubRepositoryName**. Here is a list of stories that were included:
	**PivotalProjectName** [#**PivotalStoryId**] **PivotalStoryName**
```
