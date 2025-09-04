from flask import Flask, render_template, redirect, url_for, flash, request, session
from datetime import datetime
from config import Config
from models import db, User, HelpRequest, Message

# 创建Flask应用
app = Flask(__name__)
app.config.from_object(Config)

# 初始化数据库
db.init_app(app)  # 使用 init_app 而不是直接传递 app

# 时间显示过滤器
@app.template_filter('time_ago')
def time_ago(dt):
    if not dt:
        return "未知时间"
    now = datetime.utcnow()
    diff = now - dt

    if diff.days > 365:
        return f'{diff.days // 365}年前'
    elif diff.days > 30:
        return f'{diff.days // 30}个月前'
    elif diff.days > 0:
        return f'{diff.days}天前'
    elif diff.seconds > 3600:
        return f'{diff.seconds // 3600}小时前'
    elif diff.seconds > 60:
        return f'{diff.seconds // 60}分钟前'
    else:
        return '刚刚'

# 用户认证辅助函数
def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

# 添加上下文处理器，让所有模板都能访问 current_user
@app.context_processor
def inject_current_user():
    return dict(current_user=get_current_user())

#使用 @login_required 装饰器来保护所有需要登录的页面
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
@app.route('/index')  # 添加这一行，让 /index 也指向首页
@login_required
def home():
    """首页"""
    recent_helps = HelpRequest.query.order_by(HelpRequest.created_at.desc()).limit(5).all()
    current_user = get_current_user()
    return render_template('index.html', recent_helps=recent_helps, current_user=current_user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        user_type = request.form.get('user_type', 'disabled')

        # 验证数据
        if not all([username, email, password]):
            flash('请填写所有必填字段', 'danger')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('两次输入的密码不一致', 'danger')
            return redirect(url_for('register'))

        # 检查用户是否已存在
        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('邮箱已被注册', 'danger')
            return redirect(url_for('register'))

        # 创建新用户
        new_user = User(
            username=username,
            email=email,
            user_type=user_type
        )
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('注册成功！请登录', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('注册失败，请重试', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            user.is_online = True
            db.session.commit()

            flash('登录成功！', 'success')
            return redirect(url_for('home'))
        else:
            flash('用户名或密码错误', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    """用户退出登录"""
    user_id = session.pop('user_id', None)
    if user_id:
        user = User.query.get(user_id)
        if user:
            user.is_online = False
            db.session.commit()

    flash('您已成功退出登录', 'info')
    return redirect(url_for('home'))


@app.route('/help/create', methods=['GET', 'POST'])
@login_required
def create_help():
    """发布求助"""
    current_user = get_current_user()

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')

        if not all([title, description, category]):
            flash('请填写所有必填字段', 'danger')
            return redirect(url_for('create_help'))

        new_help = HelpRequest(
            title=title,
            description=description,
            category=category,
            user_id=current_user.id
        )

        try:
            db.session.add(new_help)
            db.session.commit()
            flash('求助发布成功！', 'success')
            return redirect(url_for('help_list'))
        except Exception as e:
            db.session.rollback()
            flash('发布失败，请重试', 'danger')
            return redirect(url_for('create_help'))

    return render_template('create_help.html', current_user=current_user)


@app.route('/help')
def help_list():
    """求助列表"""
    category = request.args.get('category', '')
    status = request.args.get('status', '')
    current_user = get_current_user()

    # 构建查询
    query = HelpRequest.query

    if category:
        query = query.filter_by(category=category)
    if status:
        query = query.filter_by(status=status)

    help_requests = query.order_by(HelpRequest.created_at.desc()).all()
    return render_template('help_list.html', help_requests=help_requests, current_user=current_user)


@app.route('/help/<int:help_id>')
def help_detail(help_id):
    """求助详情"""
    help_request = HelpRequest.query.get_or_404(help_id)
    current_user = get_current_user()
    return render_template('help_detail.html', help_request=help_request, current_user=current_user)


# 初始化数据库
def init_db():
    # 在视图函数中，Flask会自动创建应用上下文
    # 在脚本中（如初始化时），没有自动的Web请求上下文
    # 所以需要手动创建应用上下文
    with app.app_context():     # ← 创建应用上下文
        db.create_all()         # ← 现在db知道它属于哪个app了
                                # 只创建不存在的表，不会影响已有表和数据

        # 添加一些测试数据（可选）
        if not User.query.first():
            # 创建测试用户
            disabled_user = User(
                username='test_user',
                email='user@test.com',
                user_type='disabled'
            )
            disabled_user.set_password('password123')

            volunteer_user = User(
                username='test_volunteer',
                email='volunteer@test.com',
                user_type='volunteer',
                skills='visual_assistance,sign_language_basic'
            )
            volunteer_user.set_password('password123')

            db.session.add(disabled_user)
            db.session.add(volunteer_user)
            db.session.commit()

            # 创建测试求助
            help_request = HelpRequest(
                title='需要帮助阅读药品说明书',
                description='我视力不好，看不清药品说明书上的小字，需要有人帮我阅读一下内容。',
                category='visual',
                user_id=disabled_user.id
            )
            db.session.add(help_request)
            db.session.commit()

if __name__=='__main__':
    init_db()
    app.run(debug=True)