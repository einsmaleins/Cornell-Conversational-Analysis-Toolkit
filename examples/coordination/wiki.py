# This example uses the wikipedia conversations corpus to reproduce figure 1
#   from the echoes of power paper (https://www.cs.cornell.edu/~cristian/Echoes_of_power.html).
#
# The plots answer these questions: 
# - Do users on the whole coordinate more to admins or nonadmins?
# - Do admins coordinate to other people more than nonadmins do?

from convokit import Utterance, Corpus, Coordination, download

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# load corpus
corpus = Corpus(filename=download("wiki-corpus"))

# split users by whether they are an admin
# this means that if a user has spoken in the corpus as both an admin and
#   a non-admin, then we will split this user into two users, one for each of
#   these roles
corpus.subdivide_users_by_attribs(["is-admin"])

# create coordination object
coord = Coordination(corpus)

# helper function to compute two coordination scores and plot them against each
#   other as a chart
# a is a tuple (speakers, targets)
# b is a tuple (speakers, targets)
# the function will compute and plot the coordination scores for the two
#   speaker-target pairs, on aggregate and by coordination marker
def compare_coordination(a, b, a_description, b_description, a_color="b", b_color="g"):
    a_speakers, a_targets = a
    b_speakers, b_targets = b
    # compute all scores for the first set of speakers and targets
    a_scores = coord.score(a_speakers, a_targets, utterances_thresh_indiv=4,
            target_thresh=1)
    _, a_score_by_marker, a_agg1, a_agg2, a_agg3 = coord.score_report(a_scores)

    # compute all scores for the second set of speakers and targets
    b_scores = coord.score(b_speakers, b_targets, utterances_thresh_indiv=4,
            target_thresh=1)
    _, b_score_by_marker, b_agg1, b_agg2, b_agg3 = coord.score_report(b_scores)

    # the rest plots this data as a double bar graph
    a_data_points = sorted(a_score_by_marker.items())
    b_data_points = sorted(b_score_by_marker.items())
    a_data_points, b_data_points = zip(*sorted(zip(a_data_points, b_data_points),
        key=lambda x: x[0][1], reverse=True))
    labels, a_data_points = zip(*a_data_points)
    _, b_data_points = zip(*b_data_points)

    labels = ["aggregate 1", "aggregate 2", "aggregate 3"] + list(labels)
    a_data_points = [a_agg1, a_agg2, a_agg3] + list(a_data_points)
    b_data_points = [b_agg1, b_agg2, b_agg3] + list(b_data_points)

    fig, ax = plt.subplots()
    ax.set_xticks(np.arange(len(a_data_points)) + 0.35)
    ax.set_xticklabels(labels, rotation="vertical")

    ax.bar(np.arange(len(a_data_points)), a_data_points, 0.35, color=a_color)
    ax.bar(np.arange(len(b_data_points)) + 0.35, b_data_points, 0.35, color=b_color)

    a_scores_a1 = [s for s in a_scores if len(a_scores[s]) == 8]
    b_scores_a1 = [s for s in b_scores
            if len(b_scores[s]) == 8]
    b_patch = mpatches.Patch(color="b",
                             label=a_description + " (total: " +
                             str(len(a_scores_a1)) + ", " +
                             str(len(a_scores)) + ")")
    g_patch = mpatches.Patch(color="g",
                             label=b_description + " (total: "  +
                             str(len(b_scores_a1)) + ", " +
                             str(len(b_scores)) + ")")
    plt.legend(handles=[b_patch, g_patch])
    plt.show()

# get all groups of users that we want to compare
everyone = corpus.users()
admins = corpus.users(lambda u: u.info["is-admin"])
nonadmins = everyone - admins

# do users on the whole coordinate more to admins or nonadmins?
compare_coordination((everyone, admins), (everyone, nonadmins),
        "Target: admins", "Target: nonadmins")
# do admins coordinate to other people more than nonadmins do?
compare_coordination((admins, everyone), (nonadmins, everyone),
        "Speaker: admins", "Speaker: nonadmins")