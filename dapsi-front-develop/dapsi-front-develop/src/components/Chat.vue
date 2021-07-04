<template>
  <div class="relative flex flex-col justify-end">
    <!-- lista de los escrito en el chat -->
    <div class="gradient"></div>
    <div
      ref="chatList"
      :class="listStyle"
      class="flex flex-col flex-1 h-full overflow-y-auto pt-5">

      <div
        v-for="(item, index) in messages" :key="index"
        :class="[
          {'item-user': item.is_customer},
          {'item-input': !input},
          {'item-bot': !item.is_customer && item.type !== 'card' && item.type !== 'button'}
        ]"
        class="item flex mt-4">

        <div
          v-if="item.type !== 'button' & item.type !== 'card'"
          class="flex items-end">
          <img
            v-if="!item.is_customer"
            class="avatar"
            src="../assets/avatar-chat.png">
          <div
            :class="[item.is_customer ? 'user' : 'bot']"
            class="bubble">
            <div :class="[item.is_customer ? 'right' : 'left']" class="arrow" />
            <p class="text-md" v-html="item.message" />
          </div>
        </div>

        <div v-else class="flex pl-6 relative max-w-full">
          <div class="grandie-right" />
          <div class="overflow-x-auto flex flex-1 pr-4">
            <div class="pr-4 flex">
              <button
                v-for="(child, i) in item.message"
                :key="i"
                @click="() => {
                  const text = item.type === 'card' ? child.value : child
                  _send(text)
                  _remove(index)
                }"
                class="bg-gray-100 border-gray-200 border rounded-md mr-3 px-3 py-1 cursor-pointer text-sm outline-none">
                <div v-if="item.type === 'card'" class="w-24 py-3 text-left leading-4">
                  <div class="flex justify-between mb-2">
                    <img class="w-7 bg-white" :src="_pathImage(child.company_01_img)" alt="">
                    <img src="../assets/icons/arrow-right2.png">
                    <img class="w-7 bg-white" :src="_pathImage(child.company_02_img)" alt="">
                  </div>
                  <p class="text-md" v-html="child.company_01" />
                  <p class="text-md font-semibold">Video settings</p>
                  <p class="text-md" v-html="child.company_02" />
                </div>
                <div v-else class="">
                  <p v-html="child" />
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- caja de chat -->
    <div class="pl-6">
      <textarea
        v-if="input"
        @keyup.enter="() => _send()"
        v-model="message"
        placeholder="Type a message..."
        class="bg-gray-100 border-gray-200 border w-full h-20 p-3 outline-none mt-5 rounded-md" />
    </div>

  </div>
</template>

<script>
import {mapState, mapActions, mapMutations} from 'vuex'
export default {
  name: 'Chat',
  data () {
    return {
      message: '',
      messages: []
    }
  },
  props: {
    input: {
      default: true,
    },
    listStyle: {
      default: 'max-h-80'
    }
  },
  computed: {
    ...mapState(['chatWebhook', 'chatTrigger']),
  },
  watch: {
    async chatTrigger (val) {
      if (val) {
        this._messages(val.messages)
        this.CHAT_TRIGGER(null)
      }
    }
  },
  methods: {
    ...mapActions(['action_postChatTrigger', 'action_postChatWebhook']),
    ...mapMutations(['CHAT_TRIGGER', 'CHAT_WEBHOOK']),
    _pathImage (img) {
      return require(`@/assets/company/${img}.png`)
    },
    _message (data, is_customer = false) {
      this.messages = [...this.messages, {
        is_customer,
        ...data
      }]
    },
    _handleDown () {
      const chatList = this.$refs.chatList
      setTimeout(() => {
        chatList.scrollTop = chatList.scrollHeight
      }, 100);
    },
    _remove (i) {
      this.messages.splice(i, 1)
      this._handleDown()
    },
    _messages (data) {
      data.map(item => {
        const events = item.custom?.events
        if (events) {
          events.map(event => {
            if (event.type !== 'path') {
              this._message({
                message: event.content,
                type: event.type,
              })
            } else {
              this.$router.push(event.content)
            }
          })
        } else {
          this._message({ message: item.text })
        }
      })
      this._handleDown()
    },
    async _send (val = '') {
      try {
        const message = val ? val : this.message
        this.message = ''
        this._message({message}, true)
        // respuesta del boo
        await this.action_postChatWebhook(message)
        this._messages(this.chatWebhook)
        this.CHAT_WEBHOOK(null)
        
      } catch (error) {
        console.log(`error`, error)
      }
    }
  }
}
</script>

<style lang="postcss">
  .item-input .avatar,
  .item-input .arrow {
    visibility: hidden;
  }
  .item-input:last-child .avatar,
  .item-input:last-child .arrow {
    visibility: visible;
  }

  .item-bot .avatar {
    @apply w-10 mr-2;
  }

  .item-bot:last-child .avatar {
    @apply w-16;
  }

  .item-user {
    @apply flex justify-end w-full pl-5;
  }
  .bubble {
    @apply py-3 px-3 relative rounded-md bg-gradient-to-r w-full flex
  }
  .item-bot:last-child .bubble.bot {
    @apply rounded-bl-none
  }
  .bubble.bot {
    @apply from-chat-20 to-chat-50 text-chat;
  }
  .bubble.user {
    @apply bg-primary-50 text-primary-500;
  }
  .gradient {
    @apply absolute top-0 left-0 w-full h-10 z-20;
    background: linear-gradient(180deg, rgba(255,255,255,0.9) 0%, rgba(0,0,0,0) 100%);
  }

  .grandie-right {
    @apply absolute top-0 right-0 w-4 h-full z-20;
    background: linear-gradient(270deg, rgba(255,255,255,0.9) 0%, rgba(0,0,0,0) 100%);
  }
  .arrow {
    @apply w-0 h-0 absolute bottom-0;
  }
  .arrow.left {
    left: -10px;
    border-bottom: 20px solid theme('colors.chat.20');
    border-left: 10px solid transparent;
  }
  .arrow.right {
    /* right: -10px;
    border-bottom: 20px solid theme('colors.primary.50');
    border-right: 10px solid transparent; */
  }
</style>