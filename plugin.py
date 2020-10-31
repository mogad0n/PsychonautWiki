###
# Copyright (c) 2020, mogad0n
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

from supybot import utils, plugins, ircutils, callbacks
from supybot.commands import *
import requests

try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('PsychonautWiki')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x

url = "https://api.psychonautwiki.org/graphql"


class PsychonautWiki(callbacks.Plugin):
    """Queries the Psychonautwiki api"""
    threaded = True


    @wrap(['something', optional('something')])
    def psywiki(self, irc, msg, args, name, category):
        """<drug> <category>
        fetches data on drug from psychonautwiki. Categories currently supported are name, dose, duration
        """
        categories = ['name', 'summary', 'dose', 'duration', 'effects', 'addictionPotential', 'crossTolerances', 'toxicity']
        query = { 'query' : 'query getdruginfo($name: String){substances(query: $name) {name summary toxicity addictionPotential crossTolerances effects { name } roas {name dose {units threshold heavy common { min max } light { min max } strong { min max }} duration {afterglow { min max units } comeup { min max units } duration { min max units } offset { min max units } onset { min max units }peak { min max units }total { min max units }}}}}', 'variables': {'name': name}}
        r = requests.post(url=url, json=query).json()

        def format_dose(dose, unit):
            if dose == 'N/A':
                return 'N/A'
            else:
                return f"{dose['min']}-{dose['max']} {unit}"

        def format_duration(duration, unit):
            if duration == 'N/A':
                return "N/A"
            else:
                return f"{duration['min']}-{duration['max']} {unit}"

        if r['data']:
            formatted_doses = []
            formatted_duration = []
            formatted_effects = []
            substance = r['data']['substances'][0]
            drug_name = substance['name']
            summary = substance['summary']
            toxicity = substance['toxicity']
            addictionPotential = substance['addictionPotential']
            crossTolerances = substance['crossTolerances']
            effects = substance['effects']
            for effect in effects:
                formatted_effects.append(effect['name'])
            roas = substance['roas']
            for roa in roas:
                if roa['dose']['threshold'] is not None:
                    threshold = roa['dose']['threshold']
                else:
                    threshold = 'N/A'
                if roa['dose']['heavy'] is not None:
                    heavy = roa['dose']['heavy']
                else:
                    heavy = 'N/A'
                if roa['dose']['light'] is not None:
                    light = roa['dose']['light']
                else:
                    light = 'N/A'
                if roa['dose']['common'] is not None:
                    common = roa['dose']['common']
                else:
                    common = 'N/A'
                if roa['dose']['strong'] is not None:
                    strong = roa['dose']['strong']
                else:
                    strong = 'N/A'
                unit_dose = roa['dose']['units']
                formatted_doses.append(f"{roa['name']} threshold: {threshold}{unit_dose} light: {format_dose(light, unit_dose)} common: {format_dose(common, unit_dose)} strong: {format_dose(strong, unit_dose)} heavy: {heavy}{unit_dose}")
                if roa['duration']['afterglow'] is not None:
                    afterglow = roa['duration']['afterglow']
                    unit_afterglow = roa['duration']['afterglow']['units']
                else:
                    afterglow = 'N/A'
                    unit_afterglow = 'N/A'
                if roa['duration']['comeup'] is not None:
                    comeup = roa['duration']['comeup']
                    unit_comeup = roa['duration']['comeup']['units']
                else:
                    comeup = 'N/A'
                    unit_comeup = 'N/A'

                if roa['duration']['offset'] is not None:
                    offset = roa['duration']['offset']
                    unit_offset = roa['duration']['offset']['units']
                else:
                    offset = 'N/A'
                    unit_offset = 'N/A'

                if roa['duration']['peak'] is not None:
                    peak = roa['duration']['peak']
                    unit_peak = roa['duration']['peak']['units']
                else:
                    peak = 'N/A'
                    unit_peak = 'N/A'

                if roa['duration']['onset'] is not None:
                    onset = roa['duration']['onset']
                    unit_onset = roa['duration']['onset']['units']
                else:
                    onset = 'N/A'
                    unit_onset = 'N/A'

                if roa['duration']['total'] is not None:
                    total = roa['duration']['total']
                    unit_total = roa['duration']['total']['units']
                else:
                    total = 'N/A'
                    unit_total = 'N/A'

                # if roa['duration']['duration'] in not None:
                #     duration = roa['duration']['duration']
                #     unit_duration = roa['duration']['duration']['units']
                # else:
                #     duration = 'N/A'
                #     unit_duration = 'N/A'

                formatted_duration.append(f"{roa['name']} onset: {format_duration(onset, unit_onset)} comeup: {format_duration(comeup, unit_comeup)} peak: {format_duration(peak, unit_peak)} offset: {format_duration(offset, unit_offset)} afterglow: {format_duration(afterglow, unit_afterglow)} total: {format_duration(total, unit_total)}")
            if category in categories and category == 'name':
                re = drug_name
            elif category in categories and category == 'summary':
                re = drug_name + ' ' + summary
            elif category in categories and category == 'addictionPotential':
                re = drug_name + ' ' + addictionPotential
            elif category in categories and category == 'toxicity':
                if toxicity is None:
                    re = 'N/A'
                else:
                    re = drug_name + ' ' + ', '.join(toxicity)
            elif category in categories and category == 'crossTolerances':
                if crossTolerances is None:
                    re = 'N/A'
                else:
                    re = drug_name + ' ' + ', '.join(crossTolerances)
            elif category in categories and category == 'effects':
                re = drug_name + ' ' + ', '.join(formatted_effects)
            elif category in categories and category == 'dose':
                re = drug_name + ' ' + ' | '.join(formatted_doses)
            elif category in categories and category == 'duration':
                re = drug_name + ' ' +  ' | '.join(formatted_duration)
            else:
                re = drug_name + ' ' + ', '.join(categories)
        else:
            re = "Unknown Substance"
        irc.reply(re)



Class = PsychonautWiki


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

