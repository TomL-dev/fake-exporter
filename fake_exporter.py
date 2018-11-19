#!/usr/bin/env python

#   Copyright (C) 2015 Filippo Giunchedi
#                 2015 Wikimedia Foundation
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import random
import sys
import time

from flask import Flask
from flask import request

application = Flask(__name__)

# hold metric values across requests
METRIC_VALUES = {}

WORDS = ['averse', 'dearly', 'harder', 'variate', 'nave', 'tonight',
         'species', 'aline', 'subplot', 'ideology', 'swilling', 'limp',
         'brusker', 'pigsty', 'trunks', 'headway', 'hilts', 'dike', 'balsa',
         'irons', 'endorse', 'kinsman', 'jalopies', 'sowing', 'equity',
         'nectar', 'hairier', 'unruly', 'marcher', 'anti', 'paucity', 'marks',
         'bridling', 'roaster', 'bevels', 'slaw', 'addicts', 'spriest',
         'sheet', 'foal', 'sadists', 'knight', 'optics', 'domains', 'gutting',
         'homely', 'clients', 'amperage', 'lark', 'bounce', 'dissent',
         'paging', 'tubing', 'skewers', 'zombi', 'ruled', 'turfed', 'orders',
         'squadron', 'bask', 'nymphs', 'fervid', 'foxhound', 'foghorns',
         'tracer', 'recurred', 'lockup', 'slackly', 'extracts', 'sorter',
         'borough', 'despot', 'suckled', 'unwashed', 'ships', 'staidly',
         'deserted', 'beckons', 'scapulas', 'foxglove', 'coppery', 'scrawl',
         'despoils', 'loco', 'uppercut', 'peed', 'foul', 'piddle', 'liens',
         'allot', 'posed', 'fruits', 'nutting', 'cleanses', 'lips', 'voiced',
         'acmes', 'offed', 'snobbish', 'scabrous', 'lake', 'canasta', 'wet',
         'while', 'nemeses', 'looked', 'hillside', 'bathrobe', 'rye',
         'debtors', 'topcoat', 'dogfish', 'quivered', 'glared', 'carol',
         'stomachs', 'chagrins', 'feedbags', 'lengths', 'grain', 'thyme',
         'moats', 'acidify', 'deceiver', 'clubbed', 'feasible', 'clucks',
         'booing', 'surfers', 'poll', 'internet', 'leaven', 'shutdown',
         'debuting', 'robin', 'snip', 'joules', 'botanist', 'spurting',
         'encoded', 'pores', 'varlet', 'suite', 'slims', 'vexing', 'retires'
         ]


@application.route('/metrics')
def fake_metrics():
    """Yield fake prometheus metrics.

    Each metric will be repeated random(0, metric_repeat) times, each with
    different tags (possibly none) up to random(0, max_tags).
    """

    metric_repeat = int(request.args.get('metric_repeat', 5))
    metrics = int(request.args.get('metrics', 25))
    max_tags = int(request.args.get('max_tags', 4))
    prefix = request.args.get('prefix', 'fake_')
    seed = int(request.args.get('seed', 0))

    # generate "truly" random values first, then seed the PRNG
    start_values = [random.randint(0, 2**15) for x in range(metrics)]
    random.seed(seed)

    all_tags = ['key%d' % x for x in range(max_tags)]

    result = []
    seen_metrics = {}
    while len(result) < metrics:
        m = random.choice(WORDS)
        tag_keys = all_tags[:random.randint(0, len(all_tags))]
        for repeat in range(random.randint(1, metric_repeat)):
            m_tags = ['%s="%s"' % (x, random.choice(WORDS)) for x in tag_keys]
            m_name = "%s%s{%s}" % (prefix, m, ','.join(m_tags))
            if not m_tags:
                m_name = "%s%s" % (prefix, m)

            if m_name in seen_metrics:
                break
            seen_metrics[m_name] = 1

            if m_name not in METRIC_VALUES:
                m_hash = sum([ord(x) for x in m_name])
                METRIC_VALUES[m_name] = start_values[m_hash %
                                                     len(start_values)]

            # http://users.ecs.soton.ac.uk/jn2/teaching/pythonLecture.html
            # meanIncrease, stdDevIncrease
            delta = random.normalvariate(0.2, 1.2)
            # XXX force all metrics to increase
            if delta < 0:
                delta *= -1
            METRIC_VALUES[m_name] += delta
            result.append("%s %f" % (m_name, METRIC_VALUES[m_name]))
    return '\n'.join(result) + '\n'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', default=5000, type=int)
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--debug', default=False, type=bool)
    options = parser.parse_args()

    application.run(debug=True, port=options.port, host=options.host)


if __name__ == '__main__':
    sys.exit(main())
