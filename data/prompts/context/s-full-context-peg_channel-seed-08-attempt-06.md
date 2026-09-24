## Search State

- **Seed**: 8
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 3 | 0.1270 | 0.14 | ✅ accepted |
| 5 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.0154 | 0.00 | ❌ rejected |
| 4 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 0.2606 | 0.13 | ❌ rejected |
| 3 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.2079 | 0.00 | ❌ rejected |
| 2 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 3 | 0.1261 | 0.14 | ✅ accepted |

**Proposal policy**: task_score is 0.14 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: peg_channel
- Frozen realised-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`
- Frozen object start: [0.48615778212844485, 0.11898214746703403, 0.04]
- Frozen task target: [0.48615778212844485, -0.04101785253296597, 0.04]
- Goal object position: (0.48615778212844485, -0.04101785253296597, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.48615778212844485, 0.11898214746703403, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.2, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0.2, 0.3]
objects:
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    radius_m: 0.018
    half_length_m: 0.025
  - name: channel_structure
    role: fixture
    dynamics: static
    geometry: two_parallel_walls
    inner_gap_m: 0.05
    wall_thickness_m: 0.03
    wall_height_m: 0.05
task_landmarks:
  frozen_object_start: [0.4862, 0.119, 0.04]
  frozen_task_target: [0.4862, -0.041, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.48615778212844485, 0.11898214746703403, 0.04]}
  frozen_targets: {'channel_exit': [0.48615778212844485, -0.04101785253296597, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.48615778212844485, 0.11898214746703403, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.48615778212844485, -0.04101785253296597, 0.04) | final destination targets |
| `fixture` | offset from fixture pose (0.54, 0.0, 0.035) | approach/contact targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.127) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_peg
  anchor: object
  offset:
  - 0.0
  - 0.02
  - 0.0
  weight: 0.3
- id: push_complete
  offset:
  - 0.0
  - 0.02
  - 0.0
  weight: 0.7
phases:
- id: approach_to_peg
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.02
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_peg
- id: push_peg
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.02
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.14
      - 0.18
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_complete

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_to_peg** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **push_peg** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.127
- **task_score** (E): 0.137
- **fitness_score**: 0.277  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.150

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_peg | 1.00 | 1.00 | 0.2587 |
| push_peg | 0.33 | 1.00 | 0.0978 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.514, 0.108, 0.061) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 2.000 | 296.108 | 403.471 |
| push_peg | push | 0.33 / step_budget | (0.514, 0.108, 0.061)→(0.513, 0.011, 0.053) | (0.503, 0.080, 0.034)→(0.503, 0.052, 0.031) | 0.160→0.133 | 1.00 / 1.667 | 161.362 | 208.067 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.513
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.410
- phase_score: 0.525
- phase_breakdown.push_complete_score: 0.461
- phase_breakdown.reach_peg_score: 0.674

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.479
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.410
- **Median Q (composite search score)**: 0.030
- **K-run variance**: 0.0205
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.373


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a8ce855c7f52ba2d198de8387bdd2f3b869655c206850d620daaec6ac6f298cd`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `79b30dd7102e96fb2fa0880d3932c959e04a6f943c7e87b878f77a0e54f87a94`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.9774,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_peg.approach_speed":0.05875,"push_peg.push_distance":0.17999,"push_peg.push_speed":0.04512},"optimized_scores":{"best_composite_score":0.32927,"best_fitness_score":0.47927,"best_task_score":0.41046},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":488.0,"contact_point_centroid":[0.50186,0.07191,0.00856],"force_p95":130.18115,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":131.91557,"mean_force":74.96267,"phase_index":1.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49238,0.0688,0.05202]},{"body_a":"attachment","body_b":"peg","contact_count":409.0,"contact_point_centroid":[0.50106,0.08603,0.0547],"force_p95":129.88536,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":131.40188,"mean_force":88.84544,"phase_index":1.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49187,0.08289,0.05419]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":7.0,"contact_point_centroid":[0.47496,0.11999,0.05789],"force_p95":118.80375,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":118.98938,"mean_force":98.56228,"phase_index":1.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.48627,0.12351,0.05639]},{"body_a":"peg","body_b":"channel_base_body","contact_count":466.0,"contact_point_centroid":[0.49621,0.11915,0.0094],"force_p95":0.62347,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.12904,"mean_force":0.78104,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.49129,0.17061,0.17436]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.49419,0.13694,0.05857],"force_p95":58.17831,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":58.8477,"mean_force":52.15382,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.48444,0.14377,0.05973]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.4996,0.19905,0.29705]}],"total_contact_groups":6},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49561,0.03693,0.02388],"final_tcp_position":[0.49517,-0.02169,0.03754],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":131.91557,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":491.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.11901,0.03377],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19914,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":59.12904,"phase_name":"approach_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":492.0,"raw_peak_contact_force":59.12904,"subtask_id":"reach_peg","tcp_end":[0.48445,0.14364,0.05907],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.03716,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":495.0,"n_steps_budget":1000.0,"object_pos_end":[0.49561,0.03693,0.02388],"object_pos_start":[0.49602,0.11901,0.03377],"object_to_goal_dist_end":0.11812,"object_to_goal_dist_start":0.19914,"object_z_max":0.03951,"peak_contact_force":0.69572,"phase_name":"push_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":904.0,"raw_peak_contact_force":131.91557,"subtask_id":"push_complete","tcp_end":[0.49517,-0.02169,0.03754],"tcp_start":[0.48445,0.14364,0.05907],"tcp_to_object_dist_end":0.06019,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `0a7722137b05abd45e72adac5a0a8f18d70c24ddc36cf4c70c52ed7e5618005d`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.21739,"average_solve_count":161.0,"average_success_count":161.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_peg.approach_speed":0.04823,"push_peg.push_distance":0.17981,"push_peg.push_speed":0.07154},"optimized_scores":{"best_composite_score":0.02142,"best_fitness_score":0.17142,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":62.0,"contact_point_centroid":[0.53652,0.09281,0.05965],"force_p95":544.6139,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":572.37058,"mean_force":435.25776,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.52466,0.09346,0.061]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":958.0,"contact_point_centroid":[0.53307,0.0471,0.05996],"force_p95":237.22344,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":248.66874,"mean_force":197.22381,"phase_index":1.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.52141,0.04909,0.06146]},{"body_a":"peg","body_b":"channel_base_body","contact_count":569.0,"contact_point_centroid":[0.50578,0.06302,0.00936],"force_p95":0.56481,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.57033,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.51277,0.13949,0.16272]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.50002,0.19787,0.29526]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50594,0.06294,0.00938],"force_p95":0.55213,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.54656,"phase_index":1.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.52148,0.04996,0.06147]}],"total_contact_groups":5},"final_pose_error":0.13181,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50596,0.06306,0.03383],"final_tcp_position":[0.52029,0.03196,0.06131],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":572.37058,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":597.0,"n_steps_budget":1000.0,"object_pos_end":[0.50601,0.06295,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":417.18826,"phase_name":"approach_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":665.0,"raw_peak_contact_force":572.37058,"subtask_id":"reach_peg","tcp_end":[0.52543,0.09334,0.06166],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04557,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.06306,0.03383],"object_pos_start":[0.50601,0.06295,0.03381],"object_to_goal_dist_end":0.14331,"object_to_goal_dist_start":0.14321,"object_z_max":0.03383,"peak_contact_force":243.21117,"phase_name":"push_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1958.0,"raw_peak_contact_force":248.66874,"subtask_id":"push_complete","tcp_end":[0.52029,0.03196,0.06131],"tcp_start":[0.52543,0.09334,0.06166],"tcp_to_object_dist_end":0.0439,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `bf9c239495ea25cc1b534d0795871edaef0fee72244885088104a44eb548c1a2`; realized-scene SHA-256: `11c1f773d01ee1d435c5ecc0d1531095d6f84a2c0ab26c3ff2560d4c62fcd41a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53648,0.05661,0.04]},{"name":"goal","value":[0.53648,-0.10339,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,0.05661,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53648,-0.10339,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.21875,"average_solve_count":160.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_peg.approach_speed":0.04286,"push_peg.push_distance":0.17984,"push_peg.push_speed":0.08249},"optimized_scores":{"best_composite_score":0.03035,"best_fitness_score":0.18035,"best_task_score":7e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":63.0,"contact_point_centroid":[0.54275,0.0872,0.05963],"force_p95":552.77886,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":578.91469,"mean_force":429.97602,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.53088,0.08774,0.06099]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":957.0,"contact_point_centroid":[0.53689,0.03857,0.05997],"force_p95":234.30668,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":243.61805,"mean_force":197.18353,"phase_index":1.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.52534,0.04083,0.06147]},{"body_a":"peg","body_b":"channel_base_body","contact_count":578.0,"contact_point_centroid":[0.50592,0.05659,0.00936],"force_p95":0.60142,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.57395,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.51627,0.1362,0.16252]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.50017,0.19753,0.29464]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50613,0.05663,0.00938],"force_p95":0.55192,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55777,"mean_force":0.54664,"phase_index":1.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.52545,0.04176,0.06148]}],"total_contact_groups":5},"final_pose_error":0.13012,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50612,0.05657,0.0338],"final_tcp_position":[0.52343,0.02327,0.06129],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":578.91469,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":607.0,"n_steps_budget":1000.0,"object_pos_end":[0.5061,0.05659,0.0338],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13686,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":412.00734,"phase_name":"approach_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":678.0,"raw_peak_contact_force":578.91469,"subtask_id":"reach_peg","tcp_end":[0.53169,0.08761,0.06171],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04896,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50612,0.05657,0.0338],"object_pos_start":[0.5061,0.05659,0.0338],"object_to_goal_dist_end":0.13685,"object_to_goal_dist_start":0.13686,"object_z_max":0.0338,"peak_contact_force":240.17785,"phase_name":"push_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1957.0,"raw_peak_contact_force":243.61805,"subtask_id":"push_complete","tcp_end":[0.52343,0.02327,0.06129],"tcp_start":[0.53169,0.08761,0.06171],"tcp_to_object_dist_end":0.04653,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```