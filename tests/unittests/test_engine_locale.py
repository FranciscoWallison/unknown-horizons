# ###################################################
# Copyright (C) 2008-2017 The Unknown Horizons Team
# team@unknown-horizons.org
# This file is part of Unknown Horizons.
#
# Unknown Horizons is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# ###################################################

"""Tests for Fife.get_locale() with the 'System default' language setting."""

from unittest import mock

import pytest

from horizons.engine.engine import Fife


def _get_locale(system_locale):
	fake_fife = mock.Mock()
	fake_fife.get_uh_setting.return_value = 'System default'
	with mock.patch('locale.getdefaultlocale', return_value=system_locale):
		return Fife.get_locale(fake_fife)


@pytest.mark.parametrize('system_locale, expected', [
	(('pt_BR', 'UTF-8'), 'pt_BR'),
	(('zh_TW', 'UTF-8'), 'zh_TW'),
	(('pt_PT', 'UTF-8'), 'pt'),
	(('de_DE', 'UTF-8'), 'de'),
	(('en_US', 'UTF-8'), 'en'),
	((None, None), 'en'),
])
def test_system_default_keeps_region_only_when_translated(system_locale, expected):
	assert _get_locale(system_locale) == expected


def test_explicit_language_setting_wins():
	fake_fife = mock.Mock()
	fake_fife.get_uh_setting.return_value = 'Deutsch'
	with mock.patch('locale.getdefaultlocale', return_value=('pt_BR', 'UTF-8')):
		assert Fife.get_locale(fake_fife) == 'de'
