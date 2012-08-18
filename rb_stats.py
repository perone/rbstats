import json
from collections import defaultdict
import argparse

import requests
import matplotlib.pyplot as plt
import numpy as np


def parse_req_params(pargs):
    rb_api_args = ['from-user', 'max-results', 'status']
    dparams = {}
    for key, value in pargs.iteritems():
        converted_key = key.replace('_', '-')
        if converted_key in rb_api_args:
            if value:
                dparams[converted_key] = value
    return dparams


def run_main():
    parser = argparse.ArgumentParser(description='Review Board Stats')
    parser.add_argument('base_api_url', help='The ReviewBoard base API URL')
    parser.add_argument('--from-user',
                        help='Only Review Requests by this user')
    parser.add_argument('--max-results', type=int,
                        help=('Maximum number of Review Requests to '
                              'retrieve (default: %(default)s)'),
                        default=200)
    parser.add_argument('--status',
                        choices=['discarded', 'pending', 'submitted'],
                        help=('Only retrieve Review Requests with '
                              'this status (default: %(default)s)'),
                        default='submitted')
    parser.add_argument('--colormap',
                        help=('The colormap that should be used for '
                              'the plotting (default: %(default)s)'),
                        default='jet')
    parser.add_argument('--interpolation',
                        help=('Interpolation method to use '
                              '(default: %(default)s'),
                        default='gaussian',
                        choices=['none', 'nearest', 'bilinear', 'bicubic',
                                 'hanning', 'hamming', 'gaussian'])

    args = parser.parse_args()
    req_params = parse_req_params(vars(args))

    ret = requests.get(args.base_api_url + '/review-requests',
                       params=req_params)
    js = json.loads(ret.content)

    graph_data = defaultdict(int)

    for review in js['review_requests']:
        submitter = review['links']['submitter']['title']

        for people in review['target_people']:
            reviewer = people['title']
            graph_data[(submitter, reviewer)] += 1.0

    xaxis = list(set(map(lambda x: x[0], graph_data.keys())))
    yaxis = list(set(map(lambda x: x[1], graph_data.keys())))

    arr = np.zeros((len(xaxis), len(yaxis)))

    for k, v in graph_data.items():
        x, y = k
        arr[xaxis.index(x), yaxis.index(y)] = v

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    im = ax.imshow(arr, cmap=plt.get_cmap(args.colormap),
                   interpolation=args.interpolation)
    ax.set_yticklabels(xaxis)

    tick_locs = range(len(yaxis))
    plt.xticks(tick_locs, yaxis, rotation='vertical')

    tick_locs = range(len(xaxis))
    plt.yticks(tick_locs, xaxis)

    plt.colorbar(im)
    plt.show()


if __name__ == "__main__":
    run_main()
