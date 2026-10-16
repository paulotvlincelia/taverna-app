/* Constructor verifies the kernel policy before the application main can run.
 * OS services are outside this process-level test containment (APP-004). */
#include <arpa/inet.h>
#include <crt_externs.h>
#include <errno.h>
#include <fcntl.h>
#include <mach-o/dyld.h>
#include <poll.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

static int external_errno(int family) {
    int sock = socket(family, SOCK_STREAM, 0);
    if (sock < 0) return errno;
    fcntl(sock, F_SETFL, O_NONBLOCK);
    int result;
    if (family == AF_INET) {
        struct sockaddr_in addr = {0};
        addr.sin_len = sizeof(addr); addr.sin_family = AF_INET; addr.sin_port = htons(443);
        inet_pton(AF_INET, "1.1.1.1", &addr.sin_addr);
        result = connect(sock, (void *)&addr, sizeof(addr));
    } else {
        struct sockaddr_in6 addr = {0};
        addr.sin6_len = sizeof(addr); addr.sin6_family = AF_INET6; addr.sin6_port = htons(443);
        inet_pton(AF_INET6, "2606:4700:4700::1111", &addr.sin6_addr);
        result = connect(sock, (void *)&addr, sizeof(addr));
    }
    int error = result < 0 ? errno : 0;
    close(sock);
    return error;
}

static int local_connection(void) {
    int server = socket(AF_INET, SOCK_STREAM, 0), client = -1, ok = 0;
    if (server < 0) return 0;
    struct sockaddr_in addr = {0};
    addr.sin_len = sizeof(addr); addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    socklen_t size = sizeof(addr);
    if (bind(server, (void *)&addr, size) || listen(server, 1) ||
        getsockname(server, (void *)&addr, &size)) goto done;
    client = socket(AF_INET, SOCK_STREAM, 0);
    if (client < 0) goto done;
    fcntl(client, F_SETFL, O_NONBLOCK);
    int result = connect(client, (void *)&addr, size);
    if (result && errno != EINPROGRESS) goto done;
    struct pollfd ready = {.fd = server, .events = POLLIN};
    if (poll(&ready, 1, 2000) != 1 || !(ready.revents & POLLIN)) goto done;
    fcntl(server, F_SETFL, O_NONBLOCK);
    int peer = accept(server, NULL, NULL);
    if (peer >= 0) { ok = 1; close(peer); }
done:
    if (client >= 0) close(client);
    close(server);
    return ok;
}

__attribute__((constructor)) static void taverna_guard(void) {
    if (strcmp(getprogname(), "SimpleX") != 0) return;
    const char *logpath = getenv("TAVERNA_GUARD_LOG");
    int fd = logpath ? open(logpath, O_WRONLY | O_CREAT | O_APPEND, 0600) : -1;
    if (fd < 0) _exit(78);
    if (getenv("TAVERNA_SANDBOX_APPLIED")) {
        int ipv4 = external_errno(AF_INET), ipv6 = external_errno(AF_INET6);
        int local = local_connection();
        dprintf(fd, "{\"pid\":%d,\"executable\":\"SimpleX\",\"phase\":\"before_main\","
            "\"ipv4_errno\":%d,\"ipv6_errno\":%d,\"loopback\":%s}\n",
            getpid(), ipv4, ipv6, local ? "true" : "false");
        close(fd);
        if ((ipv4 != EPERM && ipv4 != EACCES) ||
            (ipv6 != EPERM && ipv6 != EACCES) || !local) _exit(78);
        unsetenv("DYLD_INSERT_LIBRARIES");
        return;
    }
    const char *helper = getenv("TAVERNA_HOST_GUARD");
    char path[4096]; uint32_t size = sizeof(path);
    if (!helper || _NSGetExecutablePath(path, &size)) _exit(78);
    int argc = *_NSGetArgc(); char **argv = *_NSGetArgv();
    char **args = calloc((size_t)argc + 2, sizeof(char *));
    if (!args) _exit(78);
    args[0] = (char *)helper; args[1] = path;
    for (int i = 1; i < argc; i++) args[i + 1] = argv[i];
    close(fd);
    const char *vars[] = {"DYLD_ROOT_PATH", "DYLD_INSERT_LIBRARIES",
        "DYLD_LIBRARY_PATH", "DYLD_FRAMEWORK_PATH", "DYLD_SHARED_CACHE_DIR", "DYLD_SHARED_REGION"};
    for (int i = 0; i < 6; i++) {
        char name[128]; snprintf(name, sizeof(name), "TAVERNA_SAVED_%s", vars[i]);
        const char *value = getenv(vars[i]);
        if (value) setenv(name, value, 1);
        unsetenv(vars[i]);
    }
    execv(helper, args);
    _exit(78);
}
