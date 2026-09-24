## Search State

- **Seed**: 2
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4217 | 0.43 | ✅ accepted |
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.1880 | 0.00 | ❌ rejected |
| 10 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.3436 | 0.34 | ❌ rejected |
| 9 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 6 | -0.2048 | 0.00 | ❌ rejected |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.1257 | 0.06 | ❌ rejected |

**Proposal policy**: task_score is 0.43 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`
- Frozen object start: [0.48092897073994534, 0.06387929147312987, 0.04]
- Frozen task target: [0.48092897073994534, -0.09612070852687013, 0.04]
- Goal object position: (0.48092897073994534, -0.09612070852687013, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.48092897073994534, 0.06387929147312987, 0.04)
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
  frozen_object_start: [0.4809, 0.0639, 0.04]
  frozen_task_target: [0.4809, -0.0961, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.48092897073994534, 0.06387929147312987, 0.04]}
  frozen_targets: {'channel_exit': [0.48092897073994534, -0.09612070852687013, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7

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
| `object` | offset from object initial position (0.48092897073994534, 0.06387929147312987, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.48092897073994534, -0.09612070852687013, 0.04) | final destination targets |
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

## Current Skill (Q=0.422) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_contact
  anchor: object
  offset:
  - 0.0
  - 0.02
  - 0.005
  weight: 0.3
- id: push_channel
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_above_peg
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.05
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_contact
- id: descend_contact
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.02
    - 0.005
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_backset_y:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.y
        mode: replace
    descend_lateral_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
  guards:
  - id: guard_contact
    when: after_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: abort
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_contact
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.005
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: push_channel

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above_peg** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_contact** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.02, 0.005], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_backset_y: status=consumed; consumers=target.offset.y (replace)
    - descend_lateral_x: status=consumed; consumers=target.offset.x (replace)
  - guards:
    - id=guard_contact, when=after_phase, predicate=contact_detected, on_failure=abort, threshold=1.0
  - retries: max_attempts=0, strategy=repeat
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.005], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=reduce_speed

## Design Metrics

- **Composite score**: 0.422
- **task_score** (E): 0.433
- **fitness_score**: 0.652  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_peg | 1.00 | 1.00 | 0.1715 |
| descend_contact | 1.00 | 1.00 | 0.1089 |
| push_to_goal | 1.00 | 1.00 | 0.1595 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.493, 0.128, 0.147) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.371 | 57.501 |
| descend_contact | descend | 1.00 / step_budget | (0.493, 0.128, 0.147)→(0.503, 0.099, 0.046) | (0.498, 0.068, 0.034)→(0.498, 0.064, 0.035) | 0.148→0.144 | 1.00 / 3.667 | 122.080 | 130.186 |
| push_to_goal | push | 1.00 / step_budget | (0.503, 0.099, 0.046)→(0.501, -0.061, 0.045) | (0.498, 0.064, 0.035)→(0.498, -0.079, 0.035) | 0.144→0.012 | 1.00 / 1.000 | 0.547 | 3.659 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.859
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.638
- phase_score: 0.803
- phase_breakdown.reach_contact_score: 0.528
- phase_breakdown.push_channel_score: 0.921

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.737
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.638
- **Median Q (composite search score)**: 0.391
- **K-run variance**: 0.0037
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.398


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `6269840a353345700ffa70ea476a3ad730b138bf2ec3c52304c054f0e194e023`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a2936262b79fcd5a49fda15d77b54223f43c58bfee2e71dc505f8a2f79369706`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3027,"average_solve_count":185.0,"average_success_count":185.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_peg.approach_height":0.10277,"descend_contact.descend_backset_y":0.04231,"descend_contact.descend_lateral_x":0.01372,"push_to_goal.push_speed":0.02147},"optimized_scores":{"best_composite_score":0.50718,"best_fitness_score":0.73718,"best_task_score":0.63783},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":402.0,"contact_point_centroid":[0.49731,-0.01619,0.0451],"force_p95":114.86757,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":116.84179,"mean_force":48.95453,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49984,-0.00516,0.04307]},{"body_a":"peg","body_b":"channel_base_body","contact_count":124.0,"contact_point_centroid":[0.49302,-0.10153,0.03535],"force_p95":103.72886,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":104.43911,"mean_force":87.6165,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50231,-0.05047,0.04528]},{"body_a":"peg","body_b":"channel_base_body","contact_count":385.0,"contact_point_centroid":[0.49358,-0.02901,0.00958],"force_p95":57.63377,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.84212,"mean_force":31.75721,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50016,0.0,0.04343]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":301.0,"contact_point_centroid":[0.47481,-0.02091,0.02689],"force_p95":27.47659,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.22724,"mean_force":10.24259,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50019,-0.00385,0.04333]},{"body_a":"peg","body_b":"channel_base_body","contact_count":279.0,"contact_point_centroid":[0.49577,0.06372,0.00935],"force_p95":0.66236,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.57581,"phase_index":0.0,"phase_name":"approach_above_peg","phase_type":"approach","tcp_position_centroid":[0.48961,0.16015,0.22426]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_above_peg","phase_type":"approach","tcp_position_centroid":[0.49924,0.19771,0.29585]},{"body_a":"peg","body_b":"channel_base_body","contact_count":397.0,"contact_point_centroid":[0.49493,0.06409,0.0094],"force_p95":0.55025,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55295,"mean_force":0.54574,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.49062,0.11596,0.10208]}],"total_contact_groups":7},"final_pose_error":0.01987,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49188,-0.07354,0.03549],"final_tcp_position":[0.50447,-0.06074,0.04698],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":116.84179,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":306.0,"n_steps_budget":1000.0,"object_pos_end":[0.49525,0.06394,0.03391],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14415,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.5439,"phase_name":"approach_above_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":397.0,"raw_peak_contact_force":0.55295,"subtask_id":"reach_contact","tcp_end":[0.48122,0.12489,0.15943],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14023,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":397.0,"n_steps_budget":810.0,"object_pos_end":[0.49499,0.06366,0.03397],"object_pos_start":[0.49525,0.06394,0.03391],"object_to_goal_dist_end":0.14387,"object_to_goal_dist_start":0.14415,"object_z_max":0.03397,"peak_contact_force":109.69974,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1212.0,"raw_peak_contact_force":116.84179,"subtask_id":"reach_contact","tcp_end":[0.50246,0.10738,0.04642],"tcp_start":[0.48122,0.12489,0.15943],"tcp_to_object_dist_end":0.04607,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":527.0,"n_steps_budget":1000.0,"object_pos_end":[0.49188,-0.07354,0.03549],"object_pos_start":[0.49499,0.06366,0.03397],"object_to_goal_dist_end":0.01132,"object_to_goal_dist_start":0.14387,"object_z_max":0.04008,"peak_contact_force":0.54637,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":307.0,"raw_peak_contact_force":2.44546,"subtask_id":"push_channel","tcp_end":[0.50447,-0.06074,0.04698],"tcp_start":[0.50246,0.10738,0.04642],"tcp_to_object_dist_end":0.02132,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `78f29ebb38dd2df9149fb0cd7c7c33d55e802bb94eee599b284bb0b197a04fb7`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.09677,"average_solve_count":186.0,"average_success_count":186.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_peg.approach_height":0.06919,"descend_contact.descend_backset_y":0.02581,"descend_contact.descend_lateral_x":0.01552,"push_to_goal.push_speed":0.02158},"optimized_scores":{"best_composite_score":0.36728,"best_fitness_score":0.59728,"best_task_score":0.31503},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":275.0,"contact_point_centroid":[0.49652,-0.00557,0.04634],"force_p95":67.2417,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":79.07183,"mean_force":18.09798,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49798,0.00586,0.04038]},{"body_a":"peg","body_b":"channel_base_body","contact_count":38.0,"contact_point_centroid":[0.49343,-0.10167,0.04796],"force_p95":75.97994,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":78.42342,"mean_force":52.24966,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49713,-0.05667,0.04034]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":248.0,"contact_point_centroid":[0.47476,-0.01273,0.0373],"force_p95":38.22713,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.9843,"mean_force":8.61808,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49818,0.0162,0.04048]},{"body_a":"peg","body_b":"channel_base_body","contact_count":169.0,"contact_point_centroid":[0.49573,-0.0234,0.00967],"force_p95":25.01696,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.19027,"mean_force":8.16135,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49817,0.01646,0.04054]},{"body_a":"peg","body_b":"channel_base_body","contact_count":359.0,"contact_point_centroid":[0.49435,0.05871,0.00939],"force_p95":0.55061,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.43045,"mean_force":0.57455,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.48354,0.10293,0.08363]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.49837,0.07637,0.04468],"force_p95":4.79694,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.87763,"mean_force":2.33625,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.50112,0.08799,0.04434]},{"body_a":"peg","body_b":"channel_base_body","contact_count":339.0,"contact_point_centroid":[0.49443,0.05901,0.00933],"force_p95":0.61187,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.58936,"phase_index":0.0,"phase_name":"approach_above_peg","phase_type":"approach","tcp_position_centroid":[0.48274,0.15691,0.207]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_above_peg","phase_type":"approach","tcp_position_centroid":[0.49871,0.1972,0.29407]}],"total_contact_groups":8},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49339,-0.08905,0.03524],"final_tcp_position":[0.49701,-0.06089,0.04013],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":79.07183,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":368.0,"n_steps_budget":1000.0,"object_pos_end":[0.49411,0.05886,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13912,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.53162,"phase_name":"approach_above_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":364.0,"raw_peak_contact_force":5.43045,"subtask_id":"reach_contact","tcp_end":[0.46812,0.11851,0.12628],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11303,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":359.0,"n_steps_budget":660.0,"object_pos_end":[0.49385,0.05853,0.03389],"object_pos_start":[0.49411,0.05886,0.03385],"object_to_goal_dist_end":0.1388,"object_to_goal_dist_start":0.13912,"object_z_max":0.03389,"peak_contact_force":79.07183,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":730.0,"raw_peak_contact_force":79.07183,"subtask_id":"reach_contact","tcp_end":[0.50145,0.08768,0.04356],"tcp_start":[0.46812,0.11851,0.12628],"tcp_to_object_dist_end":0.03164,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":421.0,"n_steps_budget":1000.0,"object_pos_end":[0.49339,-0.08905,0.03524],"object_pos_start":[0.49385,0.05853,0.03389],"object_to_goal_dist_end":0.01217,"object_to_goal_dist_start":0.1388,"object_z_max":0.03971,"peak_contact_force":0.54862,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":374.0,"raw_peak_contact_force":4.20518,"subtask_id":"push_channel","tcp_end":[0.49701,-0.06089,0.04013],"tcp_start":[0.50145,0.08768,0.04356],"tcp_to_object_dist_end":0.02881,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ecba62e37d233197bb248f7fe6e722b45204af5e83240a6f27138a89bcccfe42`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29891,"average_solve_count":184.0,"average_success_count":184.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_peg.approach_height":0.09928,"descend_contact.descend_backset_y":0.01606,"descend_contact.descend_lateral_x":-0.00574,"push_to_goal.push_speed":0.02926},"optimized_scores":{"best_composite_score":0.39075,"best_fitness_score":0.62075,"best_task_score":0.3457},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":405.0,"contact_point_centroid":[0.5043,-0.04698,0.04492],"force_p95":190.18231,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":194.64521,"mean_force":113.00861,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49993,-0.03742,0.04378]},{"body_a":"peg","body_b":"channel_base_body","contact_count":377.0,"contact_point_centroid":[0.50741,0.0822,0.00919],"force_p95":140.30076,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":166.51871,"mean_force":21.87703,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.51277,0.11894,0.09673]},{"body_a":"attachment","body_b":"peg","contact_count":71.0,"contact_point_centroid":[0.51226,0.09554,0.05489],"force_p95":163.63733,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":165.98901,"mean_force":113.35809,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.50398,0.10349,0.0543]},{"body_a":"peg","body_b":"channel_base_body","contact_count":241.0,"contact_point_centroid":[0.50891,-0.10202,0.04013],"force_p95":141.85982,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":147.05685,"mean_force":109.72904,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50072,-0.05245,0.04464]},{"body_a":"peg","body_b":"channel_base_body","contact_count":582.0,"contact_point_centroid":[0.50664,-0.04229,0.00921],"force_p95":119.63459,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":122.44548,"mean_force":52.51015,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.5,-0.00917,0.04373]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":393.0,"contact_point_centroid":[0.52569,-0.06129,0.03449],"force_p95":51.73957,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.5886,"mean_force":27.86542,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49998,-0.03841,0.04385]},{"body_a":"peg","body_b":"channel_base_body","contact_count":281.0,"contact_point_centroid":[0.50539,0.08086,0.00934],"force_p95":0.60342,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.60106,"phase_index":0.0,"phase_name":"approach_above_peg","phase_type":"approach","tcp_position_centroid":[0.51438,0.16767,0.22192]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_above_peg","phase_type":"approach","tcp_position_centroid":[0.50087,0.19746,0.29392]}],"total_contact_groups":8},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50978,-0.07456,0.03574],"final_tcp_position":[0.5026,-0.06031,0.04657],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":194.64521,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":310.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.03764,"phase_name":"approach_above_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":448.0,"raw_peak_contact_force":166.51871,"subtask_id":"reach_contact","tcp_end":[0.52818,0.13952,0.15566],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13706,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":377.0,"n_steps_budget":810.0,"object_pos_end":[0.50655,0.06841,0.0366],"object_pos_start":[0.50598,0.0809,0.03378],"object_to_goal_dist_end":0.14859,"object_to_goal_dist_start":0.16113,"object_z_max":0.03585,"peak_contact_force":177.46764,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1621.0,"raw_peak_contact_force":194.64521,"subtask_id":"reach_contact","tcp_end":[0.50438,0.10133,0.0486],"tcp_start":[0.52818,0.13952,0.15566],"tcp_to_object_dist_end":0.03511,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":638.0,"n_steps_budget":1000.0,"object_pos_end":[0.50978,-0.07456,0.03574],"object_pos_start":[0.50655,0.06841,0.0366],"object_to_goal_dist_end":0.01197,"object_to_goal_dist_start":0.14859,"object_z_max":0.04378,"peak_contact_force":0.54565,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":317.0,"raw_peak_contact_force":4.32595,"subtask_id":"push_channel","tcp_end":[0.5026,-0.06031,0.04657],"tcp_start":[0.50438,0.10133,0.0486],"tcp_to_object_dist_end":0.01929,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```