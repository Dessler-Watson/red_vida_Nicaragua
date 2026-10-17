// Live Server is a static preview; both interfaces use the Python receiver.
(() => {
  if (['127.0.0.1', 'localhost', '[::1]'].includes(location.hostname) && location.port === '5500') {
    const target = new URL(location.pathname + location.search + location.hash, 'http://localhost:8080');
    location.replace(target.href);
  }
})();
