def main():
    import user_agent
    userAgentString = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_4; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.63 Safari/534.3'
    browser = user_agent.UserAgent.factory(userAgentString).pretty()
    print browser

if __name__ == '__main__':
    main()
