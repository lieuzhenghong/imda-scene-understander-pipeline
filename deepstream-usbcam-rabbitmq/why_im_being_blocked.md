# Why I'm being blocked

I have no understanding of the fundamental concepts undergirding 
the entire system,
and the Python sample apps and documentation make no attempt to
explain these concepts to me.

**What is User Meta? Why not using DisplayMeta?**

Lifecycle, as I understand it:

1. Get BatchMeta using `pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))`
2. Get each FrameMeta in BatchMeta
3. Get each ObjectMeta in FrameMeta
4. Generate NvDsEventMsgMeta for each ObjectMeta every 30 frames
5. Acquire UserMeta from Pool of BatchMeta using `pyds.nvds_acquire_user_meta_from_pool`
6. Attach the NvDSEventMsgMeta to the UserMeta using `user_event_meta.user_meta_data = msg.meta`
7. Set custom copy and release callbacks
8. Add user meta to frame (not sure what this is for) using `pyds.nvds.add_user_meta_to_frame`

I have the following questions:

1. What is a BatchMeta?
2. What is a UserMeta?
3. Why attach UserMeta to FrameMeta?


What is `user_meta_data` in User Meta?
Looking at the official documentation
([link](https://docs.nvidia.com/metropolis/deepstream/5.0/dev-guide/DeepStream_Development_Guide/baggage/struct__NvDsUserMeta.html#a0577ce8fda601fb72c6285c5413c2cf6)) 
gives me the following incredibly unhelpful answer:

```
void* _NvDsUserMeta::user_meta_data
Holds a pointer to user data to be attached.

See the deepstream-user-metadata-test example for usage.
```

Why do we need to `acquire_user_meta_from_pool`?

Here's the official [Python API documentation](https://docs.nvidia.com/metropolis/deepstream/python-api/Methods/methodsdoc.html?highlight=nvds_add_user_meta%20to_frame#nvds-acquire-user-meta-from-pool):

```
User must acquire the user meta from the user meta pool to

fill user metatada
```

There's no explanation of why we must acquire the user meta from the user meta pool.
And "metatada"--- did no one proofread this documentation
before it was deemed acceptable to publish?

And then what is going on when we are `add_user_meta_to_frame`?
Why do we need to add user meta to frame??
Again, I looked at the 
[official documentation](https://docs.nvidia.com/metropolis/deepstream/python-api/Methods/methodsdoc.html?highlight=nvds_add_user_meta%20to_frame#pyds.nvds_add_user_meta_to_frame)

which says

```
After acquiring and filling user metadata user must add
it to frame metadata if required at frame level with this API
```

and this is again incredibly obtuse.

*Why* must I add it to frame metadata?
*Is* it required at frame level??? Who knows??
The distinguished NVIDIA engineers certainly do, but 
I don't, seeing as nobody has ever explained this to me in the documentation.



## The Python sample apps are riddled with errors

## Conclusion

In general, all three of the 
- NVIDIA DeepStream SDK API Reference,
- NVIDIA DeepStream Plugin Manual, and
- Python sample apps

are all very unhelpful for a newcomer because they make no attempt to explain
the underlying concepts.
I don't expect the 

I am still desperately looking for a resource that will explain the pipeline to me.

## Appendix

[Asked a question on the Nvidia Developer Forums](https://forums.developer.nvidia.com/t/type-object-pyds-nvdsobjecttype-has-no-attribute-nvds-object-type-unknown/157360)