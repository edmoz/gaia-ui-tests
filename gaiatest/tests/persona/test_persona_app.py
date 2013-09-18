# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from gaiatest import GaiaTestCase
from gaiatest.apps.persona.app import Persona
from gaiatest.mocks.persona_test_user import PersonaTestUser
import time

AUDIENCE = "app://uitest.gaiamobile.org"


class TestPersonaStandard(GaiaTestCase):

    _mozId_tests_button_locator = ('link text', 'navigator.mozId tests')
    _standard_request_button_locator = ('id', 't-request')
    _app_identity_frame = ('css selector', 'iframe[src*="identity"]')

    _app_ready_event = ('css selector', 'li.ready')
    _app_login_event = ('css selector', 'li.login')
    _app_login_assertion_text = ('css selector', 'li.login div.assertion')

    def setUp(self):
        GaiaTestCase.setUp(self)
        self.connect_to_network()

        # Generate unverified PersonaTestUser account
        self.user = PersonaTestUser().create_user(
            verified=True, env={"browserid": "login.persona.org", "verifier": "www.123done.org"}
        )

    def _wait_and_click(self, element):
        self.wait_for_element_displayed(*element, timeout=120)
        btn = self.marionette.find_element(*element)
        btn.click()

    def _switch_to_app(self, element):
        """
        Switches back to app from trusted UI
        """
        self.marionette.switch_to_frame()
        self.marionette.switch_to_frame(self.app.frame)
        self.marionette.switch_to_frame(self.marionette.find_element(*element))

    def _check_for_email(self, email):
        assertions = self.marionette.find_elements(*self._app_login_assertion_text)
        print 'len of li.login', len(assertions)
        for assertion in assertions:
            print 'assertion:', assertion
            if assertion.find(email):
                return assertion

    def test_persona_standard_sign_in(self):
        """
        Test standard sign in to UI tests app
        """
        self.app = self.apps.launch('UI tests')

        # click on mozId tests
        self._wait_and_click(self._mozId_tests_button_locator)
        self._switch_to_app(self._app_identity_frame)

        # click on standard persona test
        self._wait_and_click(self._standard_request_button_locator)

        # Sign in via trusted/native UI
        persona = Persona(self.marionette)
        persona.login(self.user.email, self.user.password)

        # switch to app frame
        self._switch_to_app(self._app_identity_frame)
        self.wait_for_element_displayed(*self._app_ready_event)

        # Find the right assertion in the list of li.login
        assertion = self.wait_for_condition(_check_for_email(self.user.email))

        # Validate assertion
        # XXX hack: previous sign ins can result in multiple assertions printed, we want
        # the last one, but don't really have an event for it.  We sleep and get lucky
        # time.sleep(3)
        # assertion = self.marionette.find_elements(*self._app_login_assertion_text)[-1].text
        unpacked = persona.unpackAssertion(assertion)

        # sanity-check the assertion
        self.assertEqual(AUDIENCE, unpacked['payload']['aud'])
        self.assertEqual(self.user.email, unpacked['claim']['principal']['email'])

        # check with the verifier
        verified = persona.verifyAssertion(assertion, AUDIENCE)
        self.assertEqual(verified['status'], 'okay')
        self.assertEqual(verified['email'], self.user.email)
        self.assertEqual(verified['audience'], AUDIENCE)

