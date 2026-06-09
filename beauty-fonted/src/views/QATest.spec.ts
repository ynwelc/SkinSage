import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import QA from './QA.vue'
import axios from 'axios'

// 模拟axios
vi.mock('axios', () => ({
  default: {
    post: vi.fn()
  }
}))

describe('QA Component', () => {
  let wrapper: any

  beforeEach(() => {
    // 重置模拟
    (axios.post as vi.Mock).mockReset()
    
    // 挂载组件
    wrapper = mount(QA)
  })

  it('should render initial message', () => {
    const chatMessages = wrapper.findAll('.chat-message')
    expect(chatMessages.length).toBe(1)
    expect(chatMessages[0].find('.chat-bubble').text()).toBe('你好！我是美容AI助手，有什么可以帮助你的吗？')
  })

  it('should send message when button is clicked', async () => {
    // 模拟API响应
    (axios.post as vi.Mock).mockResolvedValue({
      data: { answer: '这是AI的回复' }
    })

    // 输入消息
    const input = wrapper.find('input')
    await input.setValue('测试问题')
    
    // 点击发送按钮
    const button = wrapper.find('.btn-primary')
    await button.trigger('click')
    
    // 检查输入框是否清空
    expect(input.element.value).toBe('')
    
    // 检查是否调用了API
    expect(axios.post).toHaveBeenCalledWith('http://localhost:8000/api/qa', {
      query: '测试问题',
      user_id: 1
    })
    
    // 检查消息是否添加到聊天记录
    const chatMessages = wrapper.findAll('.chat-message')
    expect(chatMessages.length).toBe(3) // 初始消息 + 用户消息 + AI回复
  })

  it('should handle API error', async () => {
    // 模拟API错误
    (axios.post as vi.Mock).mockRejectedValue(new Error('API Error'))

    // 输入消息并发送
    const input = wrapper.find('input')
    await input.setValue('测试问题')
    
    const button = wrapper.find('.btn-primary')
    await button.trigger('click')
    
    // 检查错误消息
    const chatMessages = wrapper.findAll('.chat-message')
    expect(chatMessages.length).toBe(3) // 初始消息 + 用户消息 + 错误消息
    expect(chatMessages[2].find('.chat-bubble').text()).toBe('抱歉，暂时无法回复您的问题，请稍后再试。')
  })

  it('should render recommended products', () => {
    const products = wrapper.findAll('.product-card')
    expect(products.length).toBe(4)
    expect(products[0].find('.product-title').text()).toBe('玻尿酸保湿精华')
  })
})
