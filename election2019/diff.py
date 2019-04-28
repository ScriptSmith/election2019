import pandas as pd
from enum import Enum


class DiffTypes(Enum):
    ADDED = 1
    REMOVED = 2
    CHANGED = 3


log_columns = ["candidate", "type", "changed_col", "before", "after"]


def diffs(prev: pd.DataFrame, curr: pd.DataFrame):
    new_log = []

    # Log removed candidates
    removed_candidates = prev.index.difference(curr.index)
    for candidate in removed_candidates:
        new_log.append({
            "candidate": candidate,
            "type": DiffTypes.REMOVED,
        })

    # Log added candidates
    added_candidates = curr.index.difference(prev.index)
    for candidate in added_candidates:
        new_log.append({
            "candidate": candidate,
            "type": DiffTypes.ADDED,
        })

    # Log changed values
    index = curr.index.intersection(prev.index)
    for prev_index, prev_candidate in prev.loc[index].iterrows():
        curr_candidate = curr.loc[[prev_index]].iloc[0]

        for column in curr.columns:
            if prev_candidate[column] != curr_candidate[column]:
                new_log.append({
                    "candidate": prev_index,
                    "type": DiffTypes.CHANGED,
                    "changed_col": column,
                    "before": prev_candidate[column],
                    "after": curr_candidate[column],
                })

    new_log_df = pd.DataFrame(new_log, columns=log_columns)
    return new_log_df


def test():
    test1 = pd.DataFrame([
        {"candidate": "Adam", "valueA": 1, "valueB": 2},
        {"candidate": "Ryan", "valueA": 3, "valueB": 4},
    ])
    test1 = test1.set_index('candidate')
    test2 = pd.DataFrame([
        {"candidate": "Adam", "valueA": 1, "valueB": 2},
        {"candidate": "Ryan", "valueA": 3, "valueB": 7},
        {"candidate": "Jane", "valueA": 5, "valueB": 6},
    ])
    test2 = test2.set_index('candidate')
    test3 = pd.DataFrame([
        {"candidate": "Adam", "valueA": 1, "valueB": 2},
        {"candidate": "Ryan", "valueA": 3, "valueB": 7},
        {"candidate": "Jane", "valueA": 5, "valueB": 8},
    ])
    test3 = test3.set_index('candidate')
    test4 = pd.DataFrame([
        {"candidate": "Adam", "valueA": 1, "valueB": 2},
        {"candidate": "Ryan", "valueA": 3, "valueB": 7},
        {"candidate": "Jane", "valueA": 5, "valueB": 6},
    ])
    test4 = test4.set_index('candidate')

    # test1 -> test2: add Jane, change Ryan.valueB 4 -> 7
    # test2 -> test3: change Jane.valueB 6 -> 8
    # test3 -> test4: change Jane.valueB 8 -> 6
    # test3 -> test4: change Jane.valueB 8 -> 6 (should be ignored

    diff1 = diffs(test1, test2)
    diff2 = diffs(test2, test3)

    output1, log1 = merge_log(test1, test2, pd.DataFrame(), diff1)
    output2, log2 = merge_log(test2, test3, pd.DataFrame(), diff1)


def merge_log(prev: pd.DataFrame, curr: pd.DataFrame, prev_log: pd.DataFrame,
              curr_log: pd.DataFrame):
    new_changes = pd.concat([prev_log, curr_log]).drop_duplicates(keep=False)

    master = prev.copy()
    for _, change in new_changes.iterrows():
        print(f"{change['candidate']}: {change['type']}")
        if change["type"] == DiffTypes.CHANGED:
            print(f"{change['changed_col']}:"
                  f" {change['before']} -> {change['after']}")

        accept = input("Accept? [Y/n]")
        if accept != "n":
            if change["type"] == DiffTypes.ADDED:
                master = master.append(curr.loc[change["candidate"]])
            elif change["type"] == DiffTypes.REMOVED:
                master = master.drop([change["candidate"]])
            elif change["type"] == DiffTypes.CHANGED:
                master.at[change["candidate"], change["changed_col"]] = change[
                    "after"]

    return master, pd.concat([prev_log, curr_log])

