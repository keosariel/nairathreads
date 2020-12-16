from flask import Blueprint, render_template
from . import errors

@errors.app_errorhandler(400)
def error_400(error):
    msg_head = "We are sorry, what you requested cannot be handled right now try again later."
    msg_body = "Bad Request"
    code=400
    page_title=f'Page Error {code}'
    return render_template('error.html',msg_head=msg_head,msg_body=msg_body,code=code,title=page_title)

@errors.app_errorhandler(401)
def error_401(error):
    msg_head = "We are sorry, what you requested cannot be handled right now try again later."
    msg_body = "Unauthorized"
    code=401
    page_title=f'Page Error {code}'
    return render_template('error.html',msg_head=msg_head,msg_body=msg_body,code=code,title=page_title)


@errors.app_errorhandler(404)
def error_404(error):
    msg_head = "We are sorry, the page you requested cannot be found."
    msg_body = "The URL may be misspelled or the page you're looking for is no longer available."
    code=404
    page_title=f'Page Error {code}'
    return render_template('error.html',msg_head=msg_head,msg_body=msg_body,code=code,title=page_title)


@errors.app_errorhandler(403)
def error_403(error):
    msg_head = "We are sorry, what you requested cannot be handled right now try again later."
    msg_body = "Request Forbidden"
    code=403
    page_title=f'Page Error {code}'
    return render_template('error.html',msg_head=msg_head,msg_body=msg_body,code=code,title=page_title)

@errors.app_errorhandler(405)
def error_405(error):
    msg_head = "We are sorry, what you requested cannot be handled right now try again later."
    msg_body = "Method Not Allowed"
    code=405
    page_title=f'Page Error {code}'
    return render_template('error.html',msg_head=msg_head,msg_body=msg_body,code=code,title=page_title)

@errors.app_errorhandler(406)
def error_406(error):
    msg_head = "We are sorry, what you requested cannot be handled right now try again later."
    msg_body = "Not Acceptable"
    code=406
    page_title=f'Page Error {code}'
    return render_template('error.html',msg_head=msg_head,msg_body=msg_body,code=code,title=page_title)


@errors.app_errorhandler(408)
def error_408(error):
    msg_head = "We are sorry, what you requested cannot be handled right now try again later."
    msg_body = "Request Time Out"
    code=408
    page_title=f'Page Error {code}'
    return render_template('error.html',msg_head=msg_head,msg_body=msg_body,code=code,title=page_title)

@errors.app_errorhandler(409)
def error_409(error):
    msg_head = "We are sorry, what you requested cannot be handled right now try again later."
    msg_body = "Conflict"
    code=409
    page_title=f'Page Error {code}'
    return render_template('error.html',msg_head=msg_head,msg_body=msg_body,code=code,title=page_title)


@errors.app_errorhandler(415)
def error_415(error):
    msg_head = "We are sorry, what you requested cannot be handled right now try again later."
    msg_body = "Unsupported Media Type"
    code=415
    page_title=f'Page Error {code}'
    return render_template('error.html',msg_head=msg_head,msg_body=msg_body,code=code,title=page_title)

@errors.app_errorhandler(429)
def error_429(error):
    msg_head = "We are sorry, what you requested cannot be handled right now try again later."
    msg_body = "Too Many Request"
    code=429
    page_title=f'Page Error {code}'
    return render_template('error.html',msg_head=msg_head,msg_body=msg_body,code=code,title=page_title)



@errors.app_errorhandler(500)
def error_500(error):
    msg_head = "We are sorry, what you requested cannot be handled right now try again later."
    msg_body = "Internal Server Error"
    code=500
    page_title=f'Page Error {code}'
    return render_template('error.html',msg_head=msg_head,msg_body=msg_body,code=code,title=page_title)


@errors.app_errorhandler(502)
def error_502(error):
    msg_head = "We are sorry, what you requested cannot be handled right now try again later."
    msg_body = "Bad GateWay"
    code=502
    page_title=f'Page Error {code}'
    return render_template('error.html',msg_head=msg_head,msg_body=msg_body,code=code,title=page_title)


@errors.app_errorhandler(503)
def error_503(error):
    msg_head = "We are sorry, what you requested cannot be handled right now try again later."
    msg_body = "Service Unavaliable"
    code=503
    page_title=f'Page Error {code}'
    return render_template('error.html',msg_head=msg_head,msg_body=msg_body,code=code,title=page_title)


@errors.app_errorhandler(504)
def error_504(error):
    msg_head = "We are sorry, what you requested cannot be handled right now try again later."
    msg_body = "GateWay TimeOut"
    code=504
    page_title=f'Page Error {code}'
    return render_template('error.html',msg_head=msg_head,msg_body=msg_body,code=code,title=page_title)


