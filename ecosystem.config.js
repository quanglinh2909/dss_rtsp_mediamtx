module.exports = {
  apps: [
    {
      name: 'backend_dss_mediamtx',
      script: './main.py',
      interpreter: './env/bin/python',  // dùng tương đối theo cwd
      cwd: './',  // hoặc bỏ qua nếu file ecosystem nằm trong cùng thư mục
      autorestart: true,
      watch: false,
    },
  ],
};
