const fs = require("fs");

const origReadlink = fs.readlink;
const origReadlinkSync = fs.readlinkSync;
const origPromisesReadlink = fs.promises ? fs.promises.readlink : null;

if (origReadlink) {
  fs.readlink = function (path, options, callback) {
    const cb = typeof options === "function" ? options : callback;
    const opts = typeof options === "function" ? undefined : options;
    origReadlink(path, opts, (err, linkString) => {
      if (err && (err.code === "EISDIR" || err.code === "UNKNOWN" || err.code === "EPERM")) {
        err.code = "EINVAL";
      }
      return cb(err, linkString);
    });
  };
}

if (origReadlinkSync) {
  fs.readlinkSync = function (path, options) {
    try {
      return origReadlinkSync(path, options);
    } catch (err) {
      if (err && typeof err === "object" && ("code" in err) && (err.code === "EISDIR" || err.code === "UNKNOWN" || err.code === "EPERM")) {
        err.code = "EINVAL";
      }
      throw err;
    }
  };
}

if (origPromisesReadlink) {
  fs.promises.readlink = async function (path, options) {
    try {
      return await origPromisesReadlink(path, options);
    } catch (err) {
      if (err && typeof err === "object" && ("code" in err) && (err.code === "EISDIR" || err.code === "UNKNOWN" || err.code === "EPERM")) {
        err.code = "EINVAL";
      }
      throw err;
    }
  };
}
