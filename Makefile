TARGET := iphone:clang:latest:15.0
ARCHS = arm64

include $(THEOS)/makefiles/common.mk

TWEAK_NAME = LucidInsta

LucidInsta_FILES = Tweak.x
LucidInsta_CFLAGS = -fobjc-arc -Wno-deprecated-declarations
LucidInsta_FRAMEWORKS = UIKit Foundation CoreGraphics QuartzCore

include $(THEOS_MAKE_PATH)/tweak.mk
