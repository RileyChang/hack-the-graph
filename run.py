from datetime import datetime, timedelta
import pytz

from git import Repo

FILENAME = 'file.txt'


def delete_all_commits(repo: Repo):
    # Get the first commit on this branch.
    # NOTE: There may be assumed pre-conditions to this being correct...
    initial_commit = repo.git.log('--reverse', '--pretty=format:%h').split()[0]

    # Reset --hard to the branch's initial commit.
    repo.git.reset(initial_commit, '--hard')


def make_commit(repo: Repo, date: datetime):
    with open(FILENAME, 'a') as f:
        f.write(str(date))
        f.write('\n')

    repo.index.add([FILENAME])
    repo.index.commit(
        f"This is a commit that definitely happened at {date}",
        author_date=date,
        commit_date=date,
    )
    print(f"Made commit at: {date}")


def get_square_map(current_day: datetime) -> list[list[datetime]]:
    """Return a 2d array of dates that matches the GitHub graph. This always returns a 7 row by 52 col graph.

    Note that 7x52 = 364, not 365. The rightmost column on the GitHub graph contains the 365th day as well
    as 0 or more days whose dates also appear on the left side of the graph."""

    result = []

    # The GitHub graph has Sundays as the top row. I'm being lazy and avoiding potential
    # edge cases (leap years?) by only going back 364 days and then traversing back to
    # the latest Sunday.

    one_year_ago = current_day - timedelta(days=364)
    while one_year_ago.weekday() != 6:  # sunday = 6
        one_year_ago = one_year_ago - timedelta(days=1)

    for i in range(7):
        row = []
        start = one_year_ago + timedelta(days=i)
        for j in range(52):
            row.append(start + timedelta(days=j * 7))
        result.append(row)

    return result


repo = Repo('.')
index = repo.index

delete_all_commits(repo)

today = datetime.now(pytz.utc)
square_to_date = get_square_map(today)

with open('art.txt', 'r') as f:
    art = [l.strip() for l in f.readlines()]

assert len(art) == 7
for row in art:
    assert len(row) == 52

for i, row in enumerate(art):
    for j, char in enumerate(row):
        if char != '.':
            make_commit(repo, square_to_date[i][j])


repo.git.push('-f')

# TODO: cron job to append to the graph
