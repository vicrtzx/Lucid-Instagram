TARGET := iphone:clang:latest:15.0
ARCHS = arm64

include $(THEOS)/makefiles/common.mk

TWEAK_NAME = LucidInsta

LucidInsta_FILES = Tweak.x
LucidInsta_CFLAGS = -fobjc-arc -O2 -fvisibility=hidden -Wno-deprecated-declarations
LucidInsta_LDFLAGS = -Wl,-dead_strip -Wl,-x
LucidInsta_FRAMEWORKS = UIKit Foundation

include $(THEOS_MAKE_PATH)/tweak.mk
