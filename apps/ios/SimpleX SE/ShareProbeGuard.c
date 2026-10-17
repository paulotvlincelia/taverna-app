/* Qualification only: explicit fixture containment before the extension main.
 * No constructor or fixture interface is compiled into device/release builds. */
#include <TargetConditionals.h>
#if DEBUG && TARGET_OS_SIMULATOR
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <limits.h>
/* Fixture instrumentation, not a kernel sandbox or a product access control.
 * Fixed native dependencies still require the independent authorization proof. */
#include <arpa/inet.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/uio.h>
#include <sys/un.h>
static int socket_test_active = 0;
static int fixture_destination(const struct sockaddr *address, socklen_t length) {
    if (!address || length < sizeof(sa_family_t)) return 0;
    if (address->sa_family == AF_UNIX) return 1;
    if (address->sa_family == AF_INET && length >= sizeof(struct sockaddr_in))
        return (ntohl(((const struct sockaddr_in *)address)->sin_addr.s_addr) >> 24) == 127;
    if (address->sa_family == AF_INET6 && length >= sizeof(struct sockaddr_in6)) {
        const struct in6_addr *a=&((const struct sockaddr_in6 *)address)->sin6_addr;
        return IN6_IS_ADDR_LOOPBACK(a) || (IN6_IS_ADDR_V4MAPPED(a) && a->s6_addr[12] == 127);
    }
    return 0;
}
static int fixture_connect(int fd, const struct sockaddr *address, socklen_t length) {
    if (socket_test_active && !fixture_destination(address, length)) { errno=EACCES; return -1; }
    return connect(fd, address, length);
}
static int fixture_connectx(int fd, const sa_endpoints_t *endpoints, sae_associd_t association,
                            unsigned int flags, const struct iovec *iov, unsigned int count,
                            size_t *written, sae_connid_t *connection) {
    if (socket_test_active && (!endpoints || !fixture_destination(endpoints->sae_dstaddr, endpoints->sae_dstaddrlen))) {
        errno=EACCES; return -1;
    }
    return connectx(fd,endpoints,association,flags,iov,count,written,connection);
}
static ssize_t fixture_sendto(int fd, const void *buffer, size_t length, int flags,
                              const struct sockaddr *address, socklen_t address_length) {
    if (socket_test_active && address && !fixture_destination(address,address_length)) { errno=EACCES; return -1; }
    return sendto(fd,buffer,length,flags,address,address_length);
}
static ssize_t fixture_sendmsg(int fd, const struct msghdr *message, int flags) {
    if (socket_test_active && message && message->msg_name &&
        !fixture_destination(message->msg_name,message->msg_namelen)) { errno=EACCES; return -1; }
    return sendmsg(fd,message,flags);
}
#define FIXTURE_INTERPOSE(replacement, original) \
__attribute__((used)) static const struct { const void *new_function; const void *old_function; } \
fixture_##original##_entry __attribute__((section("__DATA,__interpose"))) = { (const void *)&replacement, (const void *)&original };
FIXTURE_INTERPOSE(fixture_connect, connect)
FIXTURE_INTERPOSE(fixture_connectx, connectx)
FIXTURE_INTERPOSE(fixture_sendto, sendto)
FIXTURE_INTERPOSE(fixture_sendmsg, sendmsg)

static int prepare_share_guard(void) {
    char root[PATH_MAX], request[PATH_MAX], config[PATH_MAX], real[PATH_MAX];
    const char *suffix = "/apps/ios/SimpleX SE/ShareProbeGuard.c";
    const char *source = __FILE__, *cut = strstr(source, suffix);
    if (!cut || (size_t)(cut-source) >= sizeof(root)) _exit(78);
    memcpy(root, source, cut-source); root[cut-source] = 0;
    snprintf(request, sizeof(request), "%s/.build/share-probe-request.txt", root);
    FILE *input = fopen(request, "r");
    if (!input) return 0; /* normal extension lifecycle, without qualification */
    if (!fgets(config, sizeof(config), input)) _exit(78);
    char mode[32] = {0};
    fgets(mode, sizeof(mode), input);
    fclose(input); config[strcspn(config, "\r\n")] = 0;
    snprintf(request, sizeof(request), "%s/.build/access-qualification/run-", root);
    if (!realpath(config, real) || strncmp(real, request, strlen(request)) ||
        strlen(real) < 16 || strcmp(real+strlen(real)-16, "/ios/config.json")) _exit(78);
    setenv("TAVERNA_SHARE_PROBE", real, 1);
    if (strcmp(mode, "discovery\n") == 0) {
        setenv("TAVERNA_SHARE_DISCOVERY", "1", 1);
        return 0; /* UI-only control, never starts the core or accesses relays. */
    }
    if (strcmp(mode, "socket-test\n") == 0) socket_test_active = 1;
    *strrchr(real, '/') = 0;
    snprintf(request, sizeof(request), "%s/share-before-main.jsonl", real);
    setenv("TAVERNA_GUARD_LOG", request, 1);
    snprintf(request, sizeof(request), "%s/.build/attempts/guard/host-sandbox", root);
    setenv("TAVERNA_HOST_GUARD", request, 1);
    return 1;
}
#define TAVERNA_GUARD_EXECUTABLE "SimpleX SE"
#define TAVERNA_GUARD_PREPARE() prepare_share_guard()
#define TAVERNA_GUARD_APPLIED() (socket_test_active || getenv("TAVERNA_SANDBOX_APPLIED"))
#define TAVERNA_GUARD_MECHANISM (socket_test_active ? "test_socket_interposition" : "kernel_sandbox")
// The constructor's own control calls must pass through the same fixture filter.
#define connect fixture_connect
#include "../../../tools/taverna/ios/process-guard.c"
#undef connect
#endif
