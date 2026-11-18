#import <UIKit/UIKit.h>
#import <Foundation/Foundation.h>

static NSString *const kLucidInstaSeedKey = @"lucid_insta_seed_version";
static const NSInteger kLucidInstaSeedVersion = 2;
static NSString *const kLucidInstaLastTmpCleanKey = @"lucid_insta_last_tmp_clean_ts";

// Minimum interval between temp-directory sweeps (6 hours) and minimum file age before removal (12 hours),
// ensuring active Story/Reel camera drafts and in-flight downloads are never touched.
static const NSTimeInterval kTmpCleanCooldown = 6.0 * 3600.0;
static const NSTimeInterval kTmpStaleFileAge = 12.0 * 3600.0;

static NSDictionary<NSString *, id> *lucidInstaDefaultMap(void) {
    static NSDictionary<NSString *, id> *defaults = nil;
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        defaults = @{
            // === 1. TRUE OLED PURE BLACK & LIQUID GLASS APPEARANCE ===
            @"theme_mode": @"oled",                    // Pure #000000 OLED surfaces (0 mA on black pixels)
            @"theme_full_oled": @YES,                  // Extend pure black across secondary surfaces
            @"theme_oled_chat": @YES,                  // Pure black DM thread background
            @"theme_keyboard": @"oled",                // Matching dark/OLED keyboard

            // === 2. BATTERY, NETWORK & BACKGROUND GUARD ===
            @"disable_bg_refresh": @YES,               // Prevent background feed refresh wakeups
            @"disable_feed_autoplay": @YES,            // Prevent constant video decoding while scrolling feed
            @"disable_reels_tab_refresh": @YES,        // Stop background Reels tab refresh
            @"cache_autoclear": @YES,                  // Built-in safe cache manager
            @"cache_auto_check_size": @YES,            // Periodic non-blocking cache check
            @"cache_preserve_messages_db": @YES,       // Never wipe local DM database during cache clear
            @"api_safe_mode": @YES,                    // Request pacing & rate-limit protection
            @"api_throttle": @YES,                     // Batch/pace background GraphQL/API calls
            @"disable_haptics": @NO,                   // Keep crisp native iOS haptics
            @"bg_keepalive": @NO,                      // Strictly forbid silent audio background keepalive
            @"deleted_messages_keepalive": @NO,        // Strictly forbid background audio loop for DMs
            @"dm_keepalive": @NO,                      // Strictly forbid persistent DM socket keepalive
            @"adv_encoding_enabled": @NO,              // Direct CDN stream download (no software FFmpeg CPU drain)

            // === 3. SILENCE THIRD-PARTY UPDATER, CHANGELOG & DONATE POPUPS ===
            @"update_check_enabled": @NO,              // Stop GitHub API polling on launch
            @"whats_new_enabled": @NO,                 // Suppress external release-notes modal
            @"ryg_donate_prompt_silenced": @YES,       // Suppress third-party coffee/donation prompts

            // === 4. AD BLOCKING, META AI & SUGGESTED BLOAT REMOVAL ===
            @"hide_ads": @YES,
            @"hide_ads_feed": @YES,
            @"hide_ads_stories": @YES,
            @"hide_ads_reels": @YES,
            @"hide_ads_explore": @YES,
            @"hide_ads_shopping": @YES,
            @"hide_meta_ai": @YES,
            @"hide_meta_ai_feed": @YES,
            @"hide_meta_ai_creation": @YES,
            @"hide_meta_ai_messages": @YES,
            @"hide_meta_ai_comments": @YES,
            @"hide_meta_ai_post_menu": @YES,
            @"hide_meta_ai_search": @YES,
            @"hide_plus_upsells": @YES,                // Hide Meta Verified / Plus upsell banners
            @"hide_made_with_edits": @YES,             // Hide "Made with Edits" promotional badge
            @"hide_testflight_nag": @YES,              // Hide beta/update nags
            @"no_facebook_cards": @YES,                // Hide Facebook cross-promotion cards
            @"no_suggested_threads": @YES,
            @"hide_profile_threads_button": @YES,
            @"hide_friends_map": @YES,
            @"hide_stories_midcards": @YES,
            @"hide_suggested_stories": @YES,
            @"no_suggested_post": @YES,                // Hide algorithmic suggested posts in Home feed
            @"no_suggested_reels": @YES,               // Hide suggested Reels carousels in feed
            @"no_suggested_users": @YES,               // Hide "Suggested for you" user carousels
            @"no_suggested_chats": @YES,               // Hide suggested channels/chats in DMs

            // === 5. PRIVACY, GHOST MODE & DELETED MESSAGES ===
            @"no_seen_receipt": @YES,                  // Do not send DM read receipts automatically
            @"show_dm_seen_button": @YES,              // Manual button to mark DM as seen
            @"show_story_seen_button": @YES,           // Manual button to mark Story as seen
            @"disable_typing_status": @YES,            // Hide "typing..." indicator in DMs
            @"disable_view_once_limitations": @YES,    // Unlimited replay of view-once media
            @"keep_deleted_message": @YES,             // Preserve unsent messages locally on device
            @"strip_tracking_params": @YES,            // Strip ?igsh=... tracking params from shared URLs
            @"strip_browser_tracking": @YES,           // Strip tracking params in in-app browser
            @"adv_strip_metadata": @YES,               // Strip EXIF/device metadata from saved media

            // === 6. ACCIDENTAL TAP PROTECTION & PLAYBACK UX ===
            @"story_like_confirm": @YES,               // Confirm before liking a Story
            @"note_like_confirm": @YES,                // Confirm before liking a Note
            @"voice_call_confirm": @YES,               // Confirm before placing a voice call
            @"video_call_confirm": @YES,               // Confirm before placing a video call
            @"confirm_send_to_group": @YES,            // Confirm before sharing to group chats
            @"reels_show_scrubber": @YES,              // Always show progress scrubber on Reels
            @"reels_playback_speed": @YES,             // Enable playback speed control on Reels
            @"story_playback_seek": @YES,              // Enable scrubbing on Stories
            @"story_playback_speed": @YES,             // Enable playback speed control on Stories
            @"media_zoom_start_muted": @YES,           // Keep zoomed media muted unless unmuted

            // === 7. HIGH-QUALITY MEDIA DOWNLOADS ===
            @"download_photos": @YES,
            @"download_gallery": @YES,
            @"download_share": @YES,
            @"download_audio_message": @YES,
            @"enhance_download_quality": @YES,
            @"compact_save_sheet": @YES
        };
    });
    return defaults;
}

static void applyLucidInstaDefaults(void) {
    NSUserDefaults *store = [NSUserDefaults standardUserDefaults];
    NSDictionary<NSString *, id> *defaults = lucidInstaDefaultMap();

    // Register in NSRegistrationDomain as baseline fallback
    [store registerDefaults:defaults];

    // One-time non-destructive seed so RyukGram's own registerDefaults: cannot override Lucid defaults,
    // while preserving any setting the user explicitly customized in Lucid Insta Settings.
    if ([store integerForKey:kLucidInstaSeedKey] < kLucidInstaSeedVersion) {
        for (NSString *key in defaults) {
            if ([store objectForKey:key] == nil) {
                [store setObject:defaults[key] forKey:key];
            }
        }
        [store setInteger:kLucidInstaSeedVersion forKey:kLucidInstaSeedKey];
    }
}

static void applyPowerAndCacheBudget(void) {
    NSProcessInfo *proc = [NSProcessInfo processInfo];
    BOOL constrain = proc.lowPowerModeEnabled || proc.thermalState >= NSProcessInfoThermalStateSerious;

    NSURLCache *urlCache = [NSURLCache sharedURLCache];
    NSUInteger targetMem = constrain ? (6 * 1024 * 1024) : (20 * 1024 * 1024);
    NSUInteger targetDisk = constrain ? (64 * 1024 * 1024) : (160 * 1024 * 1024);
    if (urlCache.memoryCapacity != targetMem) urlCache.memoryCapacity = targetMem;
    if (urlCache.diskCapacity > targetDisk) urlCache.diskCapacity = targetDisk;

    if (constrain) {
        [urlCache removeAllCachedResponses];
    }
}

static void performSafeTempCleanupIfNeeded(BOOL EnteringBackground) {
    NSUserDefaults *store = [NSUserDefaults standardUserDefaults];
    NSTimeInterval now = [[NSDate date] timeIntervalSince1970];
    NSTimeInterval last = [store doubleForKey:kLucidInstaLastTmpCleanKey];
    if (last > 0 && (now - last) < kTmpCleanCooldown) {
        return;
    }
    [store setDouble:now forKey:kLucidInstaLastTmpCleanKey];

    UIApplication *app = [UIApplication sharedApplication];
    __block UIBackgroundTaskIdentifier bgTask = UIBackgroundTaskInvalid;
    if (EnteringBackground && app) {
        bgTask = [app beginBackgroundTaskWithName:@"LucidInstaSafeTmpClean" expirationHandler:^{
            if (bgTask != UIBackgroundTaskInvalid) {
                [app endBackgroundTask:bgTask];
                bgTask = UIBackgroundTaskInvalid;
            }
        }];
    }

    dispatch_async(dispatch_get_global_queue(QOS_CLASS_UTILITY, 0), ^{
        @autoreleasepool {
            NSFileManager *fm = [NSFileManager defaultManager];
            NSString *tmpDir = NSTemporaryDirectory();
            if (tmpDir.length > 0) {
                NSURL *tmpURL = [NSURL fileURLWithPath:tmpDir isDirectory:YES];
                NSArray<NSURLResourceKey> *keys = @[NSURLIsRegularFileKey, NSURLContentModificationDateKey];
                NSArray<NSURL *> *urls = [fm contentsOfDirectoryAtURL:tmpURL
                                           includingPropertiesForKeys:keys
                                                              options:NSDirectoryEnumerationSkipsHiddenFiles
                                                                error:nil];
                NSDate *cutoff = [NSDate dateWithTimeIntervalSinceNow:-kTmpStaleFileAge];
                NSSet<NSString *> *exts = [NSSet setWithObjects:@"mp4", @"mov", @"tmp", @"dat", @"part", nil];

                for (NSURL *fileURL in urls) {
                    NSString *ext = fileURL.pathExtension.lowercaseString;
                    if (![exts containsObject:ext]) continue;

                    NSNumber *isFile = nil;
                    [fileURL getResourceValue:&isFile forKey:NSURLIsRegularFileKey error:nil];
                    if (!isFile.boolValue) continue;

                    NSDate *modDate = nil;
                    [fileURL getResourceValue:&modDate forKey:NSURLContentModificationDateKey error:nil];
                    if (modDate && [modDate compare:cutoff] == NSOrderedAscending) {
                        [fm removeItemAtURL:fileURL error:nil];
                    }
                }
            }
        }
        if (bgTask != UIBackgroundTaskInvalid && app) {
            [app endBackgroundTask:bgTask];
            bgTask = UIBackgroundTaskInvalid;
        }
    });
}

%ctor {
    @autoreleasepool {
        applyLucidInstaDefaults();

        NSNotificationCenter *nc = [NSNotificationCenter defaultCenter];

        [nc addObserverForName:UIApplicationDidFinishLaunchingNotification
                        object:nil
                         queue:[NSOperationQueue mainQueue]
                    usingBlock:^(__unused NSNotification *note) {
            applyLucidInstaDefaults();
            applyPowerAndCacheBudget();
        }];

        [nc addObserverForName:UIApplicationDidEnterBackgroundNotification
                        object:nil
                         queue:[NSOperationQueue mainQueue]
                    usingBlock:^(__unused NSNotification *note) {
            performSafeTempCleanupIfNeeded(YES);
        }];

        [nc addObserverForName:UIApplicationDidReceiveMemoryWarningNotification
                        object:nil
                         queue:[NSOperationQueue mainQueue]
                    usingBlock:^(__unused NSNotification *note) {
            [[NSURLCache sharedURLCache] removeAllCachedResponses];
        }];

        [nc addObserverForName:NSProcessInfoPowerStateDidChangeNotification
                        object:nil
                         queue:[NSOperationQueue mainQueue]
                    usingBlock:^(__unused NSNotification *note) {
            applyPowerAndCacheBudget();
        }];

        if (@available(iOS 11.0, *)) {
            [nc addObserverForName:NSProcessInfoThermalStateDidChangeNotification
                            object:nil
                             queue:[NSOperationQueue mainQueue]
                        usingBlock:^(__unused NSNotification *note) {
                applyPowerAndCacheBudget();
            }];
        }
    }
}
