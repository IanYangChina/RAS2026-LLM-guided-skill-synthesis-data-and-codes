## Search State

- **Seed**: 2
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5  | 0.1832 | 0.23 | ❌ rejected |
| 13 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6  | -0.0799 | 0.00 | ❌ rejected |
| 12 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 4  | -0.0379 | 0.15 | ❌ rejected |
| 11 | approach → descend → align → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7  | 0.2213 | 0.05 | ❌ rejected |
| 10 | approach → descend → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | force_exceeded | 9  | 0.3711 | 0.38 | ✅ accepted |

**Proposal policy**: task_score is 0.38 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.371) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_behind
  anchor: object
  offset:
  - 0.0
  - 0.04
  - 0.0
  weight: 0.3
- id: push_through
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.04
    - 0.08
    orientation:
      mode: keep_current
      tolerance: 0.05
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    approach_z:
      type: scalar
      range:
      - 0.06
      - 0.12
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_behind
- id: descend_2
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.04
    - 0.0
    orientation:
      mode: keep_current
      tolerance: 0.05
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_behind
- id: push_3
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
      tolerance: 0.2
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.15
      - 0.28
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_verified
    when: after_phase
    predicate: force_below
    threshold: 5.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - -0.01
    - 0.0
  subtask_id: push_through

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.04, 0.08]
  - orientation: mode=keep_current, tolerance=0.05
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_z: status=consumed; consumers=target.offset.z (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.04, 0.0]
  - orientation: mode=keep_current, tolerance=0.05
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_3** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.2, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current, tolerance=0.2
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_verified, when=after_phase, predicate=force_below, on_failure=retry, threshold=5.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, -0.01, 0.0]

## Design Metrics

- **Composite score**: 0.371
- **task_score** (E): 0.384
- **fitness_score**: 0.651  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1881 |
| descend_2 | 1.00 | 1.00 | 0.0954 |
| push_3 | 0.33 | 1.00 | 0.1592 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.492, 0.114, 0.136) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.547 | 3.659 |
| descend_2 | descend | 1.00 / step_budget | (0.492, 0.114, 0.136)→(0.495, 0.108, 0.043) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 1.000 | 0.544 | 168.122 |
| push_3 | push | 0.33 / step_budget | (0.504, -0.018, 0.042)→(0.472, -0.139, 0.115) | (0.498, 0.068, 0.034)→(0.506, -0.072, 0.029) | 0.148→0.015 | 1.00 / 1.333 | 0.627 | 180.888 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.825
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.567
- phase_score: 0.859
- phase_breakdown.push_through_score: 0.867
- phase_breakdown.reach_behind_score: 0.842

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.742
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.567
- **Median Q (composite search score)**: 0.343
- **K-run variance**: 0.0044
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.330


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90351,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.22148,"approach_1.approach_z":0.08473,"descend_2.descend_speed":0.05424,"push_3.push_distance":0.20234,"push_3.push_speed":0.1316},"optimized_scores":{"best_composite_score":0.46233,"best_fitness_score":0.74233,"best_task_score":0.56698},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":369.0,"contact_point_centroid":[0.49603,-0.10013,0.065],"force_p95":223.80549,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":242.13751,"mean_force":179.94696,"phase_index":2.0,"phase_name":"push_3","phase_type":"push","tcp_position_centroid":[0.49373,-0.088,0.05101]},{"body_a":"attachment","body_b":"peg","contact_count":923.0,"contact_point_centroid":[0.50226,-0.02354,0.04053],"force_p95":112.43191,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":123.3683,"mean_force":54.47983,"phase_index":2.0,"phase_name":"push_3","phase_type":"push","tcp_position_centroid":[0.49351,-0.01938,0.03963]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1840.0,"contact_point_centroid":[0.50074,-0.0467,0.00844],"force_p95":80.04648,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":105.33892,"mean_force":23.99818,"phase_index":2.0,"phase_name":"push_3","phase_type":"push","tcp_position_centroid":[0.48477,-0.06971,0.07024]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":540.0,"contact_point_centroid":[0.52592,-0.00217,0.02763],"force_p95":92.32708,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":100.17659,"mean_force":41.11973,"phase_index":2.0,"phase_name":"push_3","phase_type":"push","tcp_position_centroid":[0.48998,0.0106,0.03818]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":33.0,"contact_point_centroid":[0.47497,-0.07516,0.02444],"force_p95":9.57351,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.80715,"mean_force":4.31731,"phase_index":2.0,"phase_name":"push_3","phase_type":"push","tcp_position_centroid":[0.46752,-0.15717,0.12897]},{"body_a":"peg","body_b":"channel_base_body","contact_count":482.0,"contact_point_centroid":[0.49552,0.064,0.00937],"force_p95":0.5962,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56317,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48859,0.15292,0.21119]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49923,0.19801,0.29645]},{"body_a":"peg","body_b":"channel_base_body","contact_count":335.0,"contact_point_centroid":[0.49487,0.06357,0.0094],"force_p95":0.55054,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5516,"mean_force":0.54553,"phase_index":1.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.48309,0.10673,0.08705]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.475,0.10494,0.05998],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.48687,0.10495,0.05823]}],"total_contact_groups":9},"final_pose_error":0.14762,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49343,-0.06814,0.02409],"final_tcp_position":[0.45574,-0.19585,0.17031],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":242.13751,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":509.0,"n_steps_budget":600.0,"object_pos_end":[0.49491,0.06394,0.03394],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14416,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54533,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":510.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_behind","tcp_end":[0.47934,0.10987,0.13241],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10977,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":335.0,"n_steps_budget":1000.0,"object_pos_end":[0.4953,0.06372,0.03399],"object_pos_start":[0.49491,0.06394,0.03394],"object_to_goal_dist_end":0.14392,"object_to_goal_dist_start":0.14416,"object_z_max":0.03399,"peak_contact_force":0.54632,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":336.0,"raw_peak_contact_force":0.5516,"subtask_id":"reach_behind","tcp_end":[0.48928,0.10396,0.04211],"tcp_start":[0.47934,0.10987,0.13241],"tcp_to_object_dist_end":0.04149,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1902.0,"n_steps_budget":1000.0,"object_pos_end":[0.50452,-0.06842,0.02539],"object_pos_start":[0.4953,0.06372,0.03399],"object_to_goal_dist_end":0.01918,"object_to_goal_dist_start":0.14392,"object_z_max":0.04024,"peak_contact_force":0.64203,"phase_name":"push_3","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3705.0,"raw_peak_contact_force":242.13751,"subtask_id":"push_through","tcp_end":[0.45574,-0.19585,0.17031],"tcp_start":[0.50286,-0.08794,0.04131],"tcp_to_object_dist_end":0.19905,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.83898,"average_solve_count":118.0,"average_success_count":118.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.17461,"approach_1.approach_z":0.09405,"descend_2.descend_speed":0.05766,"push_3.push_distance":0.15785,"push_3.push_speed":0.12018},"optimized_scores":{"best_composite_score":0.30817,"best_fitness_score":0.58817,"best_task_score":0.26577},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":126.0,"contact_point_centroid":[0.47498,0.1003,0.05986],"force_p95":453.45092,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":503.26453,"mean_force":394.0237,"phase_index":1.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.48521,0.10007,0.058]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":315.0,"contact_point_centroid":[0.4927,-0.10009,0.065],"force_p95":225.3578,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":282.28713,"mean_force":161.05898,"phase_index":2.0,"phase_name":"push_3","phase_type":"push","tcp_position_centroid":[0.49061,-0.08811,0.05337]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":25.0,"contact_point_centroid":[0.47497,-0.0193,0.05218],"force_p95":223.67469,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":236.70221,"mean_force":95.41795,"phase_index":2.0,"phase_name":"push_3","phase_type":"push","tcp_position_centroid":[0.48663,-0.01836,0.05004]},{"body_a":"attachment","body_b":"peg","contact_count":883.0,"contact_point_centroid":[0.50063,-0.01489,0.03809],"force_p95":120.76812,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":129.26159,"mean_force":59.72605,"phase_index":2.0,"phase_name":"push_3","phase_type":"push","tcp_position_centroid":[0.49163,-0.01103,0.0379]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1735.0,"contact_point_centroid":[0.50109,-0.04298,0.00835],"force_p95":80.02001,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":123.4921,"mean_force":24.01626,"phase_index":2.0,"phase_name":"push_3","phase_type":"push","tcp_position_centroid":[0.48557,-0.05909,0.06049]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":620.0,"contact_point_centroid":[0.52614,-0.00371,0.02538],"force_p95":100.32171,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":109.84309,"mean_force":49.54583,"phase_index":2.0,"phase_name":"push_3","phase_type":"push","tcp_position_centroid":[0.48887,0.01005,0.0367]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":19.0,"contact_point_centroid":[0.47499,-0.04435,0.02429],"force_p95":9.21118,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.32999,"mean_force":3.09502,"phase_index":2.0,"phase_name":"push_3","phase_type":"push","tcp_position_centroid":[0.48231,-0.10193,0.07125]},{"body_a":"peg","body_b":"world","contact_count":30.0,"contact_point_centroid":[0.50991,-0.04921,-0.00013],"force_p95":1.02134,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.35163,"mean_force":0.34029,"phase_index":2.0,"phase_name":"push_3","phase_type":"push","tcp_position_centroid":[0.49115,-0.03995,0.03619]},{"body_a":"peg","body_b":"channel_base_body","contact_count":492.0,"contact_point_centroid":[0.49434,0.05889,0.00935],"force_p95":0.57901,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.57594,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48182,0.15046,0.2156]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49875,0.19745,0.29561]},{"body_a":"peg","body_b":"channel_base_body","contact_count":498.0,"contact_point_centroid":[0.4943,0.059,0.00939],"force_p95":0.55026,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54601,"phase_index":1.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.4778,0.10163,0.08459]}],"total_contact_groups":11},"final_pose_error":0.12558,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49385,-0.06877,0.02415],"final_tcp_position":[0.46219,-0.17109,0.13567],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":503.26453,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":521.0,"n_steps_budget":720.0,"object_pos_end":[0.49423,0.0589,0.03387],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13915,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54987,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":527.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_behind","tcp_end":[0.46639,0.10538,0.14137],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12039,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":498.0,"n_steps_budget":1000.0,"object_pos_end":[0.49413,0.05915,0.03393],"object_pos_start":[0.49423,0.0589,0.03387],"object_to_goal_dist_end":0.1394,"object_to_goal_dist_start":0.13915,"object_z_max":0.03393,"peak_contact_force":0.53981,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":624.0,"raw_peak_contact_force":503.26453,"subtask_id":"reach_behind","tcp_end":[0.48866,0.09909,0.04201],"tcp_start":[0.46639,0.10538,0.14137],"tcp_to_object_dist_end":0.04112,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1797.0,"n_steps_budget":1000.0,"object_pos_end":[0.50469,-0.06897,0.02655],"object_pos_start":[0.49413,0.05915,0.03393],"object_to_goal_dist_end":0.01802,"object_to_goal_dist_start":0.1394,"object_z_max":0.04022,"peak_contact_force":0.56826,"phase_name":"push_3","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3627.0,"raw_peak_contact_force":282.28713,"subtask_id":"push_through","tcp_end":[0.46219,-0.17109,0.13567],"tcp_start":[0.50193,-0.08768,0.04128],"tcp_to_object_dist_end":0.15537,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45038,"average_solve_count":131.0,"average_success_count":131.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.22298,"approach_1.approach_z":0.08678,"descend_2.descend_speed":0.07373,"push_3.push_distance":0.20139,"push_3.push_speed":0.04476},"optimized_scores":{"best_composite_score":0.34275,"best_fitness_score":0.62275,"best_task_score":0.31821},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":730.0,"contact_point_centroid":[0.5028,0.01277,0.04383],"force_p95":8.95678,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.24002,"mean_force":3.45834,"phase_index":2.0,"phase_name":"push_3","phase_type":"push","tcp_position_centroid":[0.49909,0.02438,0.03818]},{"body_a":"peg","body_b":"channel_base_body","contact_count":565.0,"contact_point_centroid":[0.50617,-0.0066,0.00985],"force_p95":8.95908,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.77978,"mean_force":4.63403,"phase_index":2.0,"phase_name":"push_3","phase_type":"push","tcp_position_centroid":[0.49969,0.03767,0.03851]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":541.0,"contact_point_centroid":[0.52508,-0.0077,0.02294],"force_p95":3.41686,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.26315,"mean_force":1.22941,"phase_index":2.0,"phase_name":"push_3","phase_type":"push","tcp_position_centroid":[0.49895,0.02047,0.03813]},{"body_a":"peg","body_b":"channel_base_body","contact_count":484.0,"contact_point_centroid":[0.50567,0.08085,0.00935],"force_p95":0.56028,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.57829,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51485,0.16081,0.21117]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50038,0.19773,0.29495]},{"body_a":"peg","body_b":"channel_base_body","contact_count":276.0,"contact_point_centroid":[0.50598,0.08087,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55008,"mean_force":0.54677,"phase_index":1.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.5174,0.12293,0.08879]}],"total_contact_groups":6},"final_pose_error":0.0705,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50771,-0.07777,0.03588],"final_tcp_position":[0.49683,-0.04985,0.03755],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":18.24002,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54636,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":520.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_behind","tcp_end":[0.52984,0.12558,0.13335],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11173,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":276.0,"n_steps_budget":870.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":0.5464,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":276.0,"raw_peak_contact_force":0.55008,"subtask_id":"reach_behind","tcp_end":[0.50575,0.12068,0.04352],"tcp_start":[0.52984,0.12558,0.13335],"tcp_to_object_dist_end":0.04098,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50771,-0.07777,0.03588],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.00902,"object_to_goal_dist_start":0.16112,"object_z_max":0.03621,"peak_contact_force":0.6702,"phase_name":"push_3","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1836.0,"raw_peak_contact_force":18.24002,"subtask_id":"push_through","tcp_end":[0.49683,-0.04985,0.03755],"tcp_start":[0.50575,0.12068,0.04352],"tcp_to_object_dist_end":0.03001,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```