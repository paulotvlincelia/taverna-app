#import <UIKit/UIKit.h>
#include <arpa/inet.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <unistd.h>
@interface ControlScene : UIResponder <UIWindowSceneDelegate>
@property (strong,nonatomic) UIWindow *window;
@end
@implementation ControlScene
- (void)scene:(UIScene *)scene willConnectToSession:(UISceneSession *)session options:(UISceneConnectionOptions *)options {
 self.window=[[UIWindow alloc] initWithWindowScene:(UIWindowScene*)scene];UIViewController *vc=[UIViewController new];vc.view.backgroundColor=UIColor.systemBackgroundColor;UILabel *label=[[UILabel alloc] initWithFrame:CGRectMake(20,100,340,100)];label.text=@"Isolation control";label.textColor=UIColor.labelColor;[vc.view addSubview:label];self.window.rootViewController=vc;[self.window makeKeyAndVisible];printf("UIKIT_CONTROL_READY\n");fflush(stdout);
}
@end
@interface ControlDelegate : UIResponder <UIApplicationDelegate>
@end
@implementation ControlDelegate
- (BOOL)application:(UIApplication*)app didFinishLaunchingWithOptions:(NSDictionary*)options {
 int fd=socket(AF_INET,SOCK_STREAM,0),err=fd<0?errno:0;
 if(fd>=0){fcntl(fd,F_SETFL,O_NONBLOCK);struct sockaddr_in a={0};a.sin_len=sizeof(a);a.sin_family=AF_INET;a.sin_port=htons(443);inet_pton(AF_INET,"1.1.1.1",&a.sin_addr);err=connect(fd,(void*)&a,sizeof(a))<0?errno:0;close(fd);}
 printf("UIKIT_EXTERNAL_CONNECT_ERRNO=%d\n",err);fflush(stdout);if(err!=EPERM&&err!=EACCES)_exit(78);
 return YES;
}
- (UISceneConfiguration*)application:(UIApplication*)app configurationForConnectingSceneSession:(UISceneSession*)session options:(UISceneConnectionOptions*)options { UISceneConfiguration *c=[[UISceneConfiguration alloc] initWithName:@"Control" sessionRole:session.role];c.delegateClass=ControlScene.class;return c; }
@end
int main(int argc,char**argv){@autoreleasepool{return UIApplicationMain(argc,argv,nil,NSStringFromClass(ControlDelegate.class));}}
