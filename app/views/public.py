from flask import Blueprint, render_template, g
from database import *
from util import *

public = Blueprint('public', __name__)

@public.route("/")
def public_index():
    return render_template("index.html")

@public.route("/lobby/<int:id>")
@public.route("/lobby")
@authed()
def public_lobby(id=None):
    if id:
        try:
            lobby = Lobby.get(Lobby.id == id)
        except Lobby.DoesNotExist:
            return flashy("That lobby does not exist!")
        if not lobby.canJoin(g.user):
            return flashy("You cannt join that lobby!")
        if lobby.state == LobbyState.LOBBY_STATE_UNUSED:
            return flashy("That lobby has expired!")

        # LOL SILLY, you can't be in more than one lobby at a time! Duh!
        for lob in Lobby.select().where((Lobby.members.contains(g.uid)) & (Lobby.id != id)):
            lob.userLeave(g.user)

        lobby.joinLobby(g.user)
    return render_template("lobby.html", lobby=id)

@public.route("/friends")
@authed()
def public_friends():
    requests = list(g.user.getFriendRequests())
    friends = Friendship.select().where(((Friendship.usera == g.uid) |
        (Friendship.userb == g.uid)) &
        Friendship.active == True)
    friends = [i for i in friends]

    return render_template("friends.html",  friends=friends, requests=requests)

@public.route("/u/<user>")
def public_user(user=None):
    try:
        base_q = (User.username ** user)
        if user.isdigit():
            base_q |= (User.id == user)
        u = User.get(base_q)
    except User.DoesNotExist:
        return flashy("No such user!")

    return render_template("profile.html", user=u)

@public.route("/bans")
def public_bans():
    return render_template("bans.html")

@public.route("/about")
def public_about():
    return render_template("about.html")

@public.route("/settings")
@authed()
def public_settings():
    return render_template("settings.html", user=g.user)

@public.route("/donate")
def public_donate():
    return render_template("donate.html", user=g.user)

@public.route("/matches")
def public_matches(): pass

@public.route("/match/<int:id>")
def public_match(id):
    try:
        match = Match.get(Match.id == id)
    except Match.DoesNotExist:
        return flashy("That match does not exist!")

    level = User.select(User.level).where(User.id == g.uid).get().level
    if match.level > level:
        return flashy("You do not have permission to view that!")

    return render_template("match.html", match=id)

@public.route("/forum")
def public_forum_index():
    return render_template("forum.html")

@public.route("/forum/<fid>")
def public_forum_single(fid):
    level = g.user.level if g.user else 0

    try:
        forum = Forum.get((Forum.id == fid) & Forum.getPermQuery(level))
    except Forum.DoesNotExist:
        return flashy("Invalid Forum!")

    return render_template("forum.html", forum=forum)

@public.route("/forum/<fid>/thread/<tid>")
def public_forum_thread(fid, tid):
    level = g.user.level if g.user else 0

    try:
        forum = Forum.get((Forum.id == fid) & Forum.getPermQuery(level))
    except Forum.DoesNotExist:
        return flashy("Invalid Forum!")

    try:
        post = ForumPost.get(
            (ForumPost.forum == forum) &
            ForumPost.getThreadParentQuery() &
            ForumPost.getValidQuery() &
            (ForumPost.id == tid))
    except ForumPost.DoesNotExist:
        return flashy("Invalid Forum Thread!")

    return render_template("forum.html", forum=forum, post=post)
