# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from gaiatest import GaiaTestCase
import time


class TestGallery(GaiaTestCase):

    _gallery_items_locator = ('css selector', 'li.thumbnail')
    _current_image_locator = ('css selector', '#frames > div.frame[style ~= "translateX(0px);"] > img')
    _photos_toolbar_locator = ('id', 'fullscreen-toolbar')

    images = ['IMG_0001.jpg', 'IMG_0002.jpg', 'IMG_0003.jpg', 'IMG_0004.jpg']

    def setUp(self):
        GaiaTestCase.setUp(self)

        # add photo to storage
        for image in self.images:
            self.push_resource(image, 'DCIM/100MZLLA')

        # launch the Gallery app
        self.app = self.apps.launch('Gallery')

    def test_gallery_full_screen_image_flicks(self):
        # https://moztrap.mozilla.org/manage/case/1326/

        #wait for gallery to be available
        self.wait_for_element_displayed(*self._gallery_items_locator)

        gallery_items = self.marionette.execute_script("return window.wrappedJSObject.files;")

        self.assertEqual(len(gallery_items), len(self.images))

        # check that the first image is not a video
        for index, item in enumerate(gallery_items):
            # If the current item is not a video, set it as the gallery item to tap.
            if 'video' not in item['metadata']:
                first_gallery_item = self.marionette.find_elements(*self._gallery_items_locator)[index]
                break

        # tap first image to open full screen view
        self.marionette.tap(first_gallery_item)
        self.wait_for_element_displayed(*self._current_image_locator)

        previous_image_source = None

        # Check the next flicks
        for i in range(len(gallery_items)):

            current_image_source = self.marionette.find_element(*self._current_image_locator).get_attribute('src')
            print 'current image is: %s' % (i + 1)

            self.assertIsNotNone(current_image_source)
            self.assertNotEqual(current_image_source, previous_image_source)

            self.assertTrue(self.is_element_displayed(*self._photos_toolbar_locator))

            previous_image_source = current_image_source

            if i != len(gallery_items) - 1:
                self.flick_to_image('left')

        # try to flick next image (No image should be available)
        self.flick_to_image('left')

        current_image_source = self.marionette.find_element(*self._current_image_locator).get_attribute('src')
        print 'current image is: 4'

        self.assertIsNotNone(current_image_source)
        self.assertEqual(current_image_source, previous_image_source)

        self.assertTrue(self.is_element_displayed(*self._photos_toolbar_locator))

        previous_image_source = current_image_source

        # check the prev flick
        for i in range(len(gallery_items) - 1):

            self.flick_to_image('right')

            current_image_source = self.marionette.find_element(*self._current_image_locator).get_attribute('src')
            print 'current image is: %s' % (len(gallery_items) - i)

            self.assertIsNotNone(current_image_source)
            self.assertNotEqual(current_image_source, previous_image_source)

            self.assertTrue(self.is_element_displayed(*self._photos_toolbar_locator))

            previous_image_source = current_image_source

        # try to flick prev image (No image should be available)
        self.flick_to_image('right')

        current_image_source = self.marionette.find_element(*self._current_image_locator).get_attribute('src')
        print 'current image is: 1'

        self.assertIsNotNone(current_image_source)
        self.assertEqual(current_image_source, previous_image_source)

        self.assertTrue(self.is_element_displayed(*self._photos_toolbar_locator))

    def flick_to_image(self, direction):

        current_image = self.marionette.find_element(*self._current_image_locator)

        if direction == 'left':
            # Flick to next image
            self.marionette.flick(current_image,  # target element
                                  '50%', '50%',  # start from middle of the target element
                                  '-50%', 0,  # move 50% of width to the left
                                  800)  # gesture duration
        elif direction == 'right':
            # Flick to previous image
            self.marionette.flick(current_image,  # target element
                                  '50%', '50%',  # start from middle of the target element
                                  '+50%', 0,  # move 50% of width to the right
                                  800)  # gesture duration
        else:
            self.fail('Provided argument is invalid.\n Expected: "left" or "right"\n Actual: "%s"' % direction)

        # Wait for next image to be available
        self.wait_for_element_displayed(*self._current_image_locator)
