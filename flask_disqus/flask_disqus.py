import json
import base64
import hmac
import hashlib
import time

from flask import render_template_string, g


class Disqus(object):
    def __init__(self, app=None):
        if app:
            self.app = app
            self.init_app(app)

    def __call__(self, app, *args, **kwargs):
        pass

    def init_app(self, app):
        self.DISQUS_SECRET_KEY = str(app.config.get('DISQUS_SECRET_KEY'))
        if not self.DISQUS_SECRET_KEY:
            return "<p>You need to set DISQUS_SECRET_KEY before you can use SSO</p>"
        self.DISQUS_PUBLIC_KEY = str(app.config.get('DISQUS_PUBLIC_KEY'))
        if not self.DISQUS_PUBLIC_KEY:
            return "<p>You need to set DISQUS_PUBLIC_KEY before you can use SSO</p>"
        self.init_template_tags(app)


    def init_template_tags(self, app):

        @app.context_processor
        def _disqus_context_processor():
            def disqus_dev():
                """
                Return the HTML/js code to enable DISQUS comments on a local
                development server if settings.DEBUG is True.
                """
                disqus_url = app.config.get("SERVER_NAME")
                template = """
                {% if disqus_url %}
                    <script type="text/javascript">
                        var disqus_developer = 1;
                        var disqus_url = '{{ disqus_url }}';
                    </script>
                {% endif %}
                """
                return render_template_string(template, disqus_url=disqus_url)

            def disqus_show_comments(shortname=''):
                """
                Return the HTML code to display DISQUS comments.
                """
                shortname = str(self.app.config.get('DISQUS_WEBSITE_SHORTNAME', shortname))

                template = """
                <div id="disqus_thread"></div>
                <script type="text/javascript">
                /* <![CDATA[ */
                {% block config_variables %}
                    var disqus_shortname = '{{ shortname }}';
                {{ config|safe}}
                {% endblock %}
                    /* * * DON'T EDIT BELOW THIS LINE * * */
                    (function() {
                        var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true;
                        dsq.src = '//' + disqus_shortname + '.disqus.com/embed.js';
                        (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);
                    })();
                /* ]]> */
                </script>
                <noscript>Please enable JavaScript to view the <a href="//disqus.com/?ref_noscript">comments powered by Disqus.</a></noscript>
                <a href="//disqus.com" class="dsq-brlink">blog comments powered by <span class="logo-disqus">Disqus</span></a>
                """
                return render_template_string(template, shortname=shortname, config='')

            def disqus_sso():
                """
                Return the HTML/js code to enable DISQUS SSO - so logged in users on
                your site can be logged in to disqus seemlessly.
                """
                user = g.user

                if user.is_anonymous():
                    return ""

                # create a JSON packet of our data attributes
                data = json.dumps({
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                })
                # encode the data to base64
                message = base64.b64encode(data.encode('utf-8'))

                # generate a timestamp for signing the message
                timestamp = int(time.time())
                key = self.DISQUS_SECRET_KEY.encode('utf-8')
                msg = ('%s %s' % (message, timestamp)).encode('utf-8')
                digestmod = hashlib.sha1
                # generate our hmac signature
                sig = hmac.HMAC(key, msg, digestmod).hexdigest()
                template = """
                <script type="text/javascript">
                    var disqus_config = function() {
                        this.page.remote_auth_s3 = "{{ message }} {{ sig }} {{ timestamp }}";
                        this.page.api_key = "{{ pub_key }}";
                    }
                </script>
                """
                return render_template_string(template, message=message, timestamp=timestamp, sig=sig,
                                              pub_key=self.DISQUS_PUBLIC_KEY)

            def disqus_recent_comments(shortname='', num_items=5, excerpt_length=200, hide_avatars=0, avatar_size=32):
                """
                Return the HTML/js code which shows recent comments.
                """
                shortname = str(app.config.get('DISQUS_WEBSITE_SHORTNAME', shortname))
                template = """
                <div id="dsq-recent-comments" class="dsq-widget">
                    <script type="text/javascript">
                        {% block config_variables %}
                            var disqus_shortname = '{{ shortname }}';
                        {{ config|safe }}
                        {% endblock %}
                    </script>
                    <script src='//{{ shortname }}.disqus.com/recent_comments_widget.js?num_items={{ num_items }}&hide_avatars={{ hide_avatars }}&avatar_size={{ avatar_size }}&excerpt_length={{ excerpt_length }}'>
                    </script>
                </div>
                """
                params = {'shortname': shortname, 'num_items': num_items, 'hide_avatars': hide_avatars,
                          'avatar_size': avatar_size, 'excerpt_length': excerpt_length, 'config': ''}
                return render_template_string(template, **params)

            def disqus_num_replies(shortname=''):
                """
                Return the HTML/js code which transforms links that end with an
                #disqus_thread anchor into the threads comment count.
                """
                shortname = str(app.config.get('DISQUS_WEBSITE_SHORTNAME', shortname))
                template = """
                <script type="text/javascript">
                {% block config_variables %}
                    var disqus_shortname = '{{ shortname }}';
                {{ config|safe }}
                {% endblock %}
                    /* * * DON'T EDIT BELOW THIS LINE * * */
                    (function () {
                        var s = document.createElement('script'); s.async = true;
                        s.type = 'text/javascript';
                        s.src = '//' + disqus_shortname + '.disqus.com/count.js';
                        (document.getElementsByTagName('HEAD')[0] || document.getElementsByTagName('BODY')[0]).appendChild(s);
                    }());
                </script>
                """
                params = {
                    'shortname': shortname,
                    'config': "",
                }
                return render_template_string(template, **params)

            return {
                'disqus_dev': disqus_dev,
                'disqus_show_comments': disqus_show_comments,
                'disqus_sso': disqus_sso,
                'disqus_recent_comments': disqus_recent_comments,
                'disqus_num_replies': disqus_num_replies
            }
