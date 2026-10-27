#import <UIKit/UIKit.h>
#import <Foundation/Foundation.h>
#import <objc/runtime.h>

static void registerLucidInstaDefaults() {
    NSDictionary *defaults = @{
        // === 1. BATTERY & PERFORMANCE (Maximum optimization for iPhone 17 120Hz & OLED) ===
        @"disable_bg_refresh": @YES,               // Stop battery-draining background refresh
        @"disable_feed_autoplay": @YES,            // Disable constant auto-play in feed to save battery & GPU
        @"cache_autoclear": @YES,                  // Automatically clear cached media
        @"cache_auto_check_size": @YES,            // Check cache size periodically without blocking UI
        @"disable_reels_tab_refresh": @YES,        // Stop background refresh in Reels tab
        @"api_safe_mode": @YES,                    // Rate-limit protector & request batching
        @"api_throttle": @YES,                     // Paced API requests to prevent server flags and save power
        @"disable_haptics": @NO,                   // Keep crisp iOS haptics
        
        // === 2. AD BLOCKING & BLOAT REMOVAL (100% Clean Experience) ===
        @"hide_ads": @YES,                         // Master ad-blocking switch
        @"hide_ads_feed": @YES,                    // Hide sponsored posts in Home feed
        @"hide_ads_stories": @YES,                 // Hide story ads
        @"hide_ads_reels": @YES,                   // Hide sponsored reels
        @"hide_ads_explore": @YES,                 // Hide ads in explore grid
        @"hide_ads_shopping": @YES,                // Hide shopping tags / shopping ads
        @"hide_meta_ai": @YES,                     // Completely eliminate Meta AI buttons & prompts
        @"hide_meta_ai_creation": @YES,            // Hide Meta AI in story / post creation
        @"hide_meta_ai_messages": @YES,            // Hide Meta AI in DMs
        @"hide_meta_ai_comments": @YES,            // Hide Meta AI in comments
        @"no_suggested_threads": @YES,             // Hide Threads suggestions
        @"hide_profile_threads_button": @YES,      // Hide Threads button from profiles
        @"hide_friends_map": @YES,                 // Hide Friends Map bloat
        @"hide_stories_midcards": @YES,            // Hide suggestions between stories
        @"hide_suggested_stories": @YES,           // Hide suggested story carousels
        
        // === 3. PRIVACY & GHOST MODE (Zero Seen Traces) ===
        @"no_seen_receipt": @YES,                  // Do not send DM read receipts automatically
        @"show_dm_seen_button": @YES,              // Manual button to mark DM as seen only when desired
        @"show_story_seen_button": @YES,           // Manual button to mark stories as seen
        @"disable_typing_status": @YES,            // Hide "typing..." in DMs
        @"disable_view_once_limitations": @YES,    // Allow viewing "view once" disappearing media multiple times
        @"strip_tracking_params": @YES,            // Strip ?igsh=... spy parameters from shared links
        @"strip_browser_tracking": @YES,           // Strip tracking parameters in in-app browser
        @"adv_strip_metadata": @YES,               // Strip EXIF / device tracking from downloaded media
        
        // === 4. MEDIA DOWNLOAD & CONVENIENCE ===
        @"download_photos": @YES,                  // Download photos in full original resolution
        @"download_gallery": @YES,                 // Support 1-tap download of carousels
        @"download_share": @YES,                   // Add direct download option to share sheet
        @"download_audio_message": @YES,           // Download voice notes
        @"enhance_download_quality": @YES,         // Download highest bitrate video streams
        @"compact_save_sheet": @YES                // Minimalist save sheet
    };
    
    [[NSUserDefaults standardUserDefaults] registerDefaults:defaults];
}

// Background cache cleaner triggered asynchronously when app enters background
static void performAsyncInstagramCacheClean() {
    dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_BACKGROUND, 0), ^{
        @autoreleasepool {
            NSFileManager *fm = [NSFileManager defaultManager];
            NSString *tmpDir = NSTemporaryDirectory();
            if (tmpDir) {
                NSArray *tmpFiles = [fm contentsOfDirectoryAtPath:tmpDir error:nil];
                for (NSString *file in tmpFiles) {
                    NSString *ext = [file pathExtension].lowercaseString;
                    if ([ext isEqualToString:@"mp4"] || [ext isEqualToString:@"mov"] || 
                        [ext isEqualToString:@"tmp"] || [ext isEqualToString:@"dat"]) {
                        NSString *fullPath = [tmpDir stringByAppendingPathComponent:file];
                        [fm removeItemAtPath:fullPath error:nil];
                    }
                }
            }
        }
    });
}

%hook UIApplication
- (void)_applicationDidFinishLaunchingWithOptions:(id)arg1 {
    %orig;
    registerLucidInstaDefaults();
    performAsyncInstagramCacheClean();
}
%end

%ctor {
    registerLucidInstaDefaults();
    
    // Listen to background transition to keep storage and RAM spotless
    [[NSNotificationCenter defaultCenter] addObserverForName:UIApplicationDidEnterBackgroundNotification
                                                      object:nil
                                                       queue:[NSOperationQueue mainQueue]
                                                  usingBlock:^(NSNotification *note) {
        performAsyncInstagramCacheClean();
    }];
    
    %init;
}
