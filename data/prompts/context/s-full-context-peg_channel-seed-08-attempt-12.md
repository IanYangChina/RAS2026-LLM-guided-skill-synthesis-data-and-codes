## Search State

- **Seed**: 8
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.2339 | 0.35 | ❌ rejected |
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | contact_detected | pose_tolerance | 5 | -0.2511 | 0.00 | ❌ rejected |
| 10 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4009 | 0.37 | ✅ accepted |
| 9 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.0608 | 0.00 | ❌ rejected |
| 8 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2762 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.35 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.234) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_peg
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.002
  weight: 0.3
- id: push_complete
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
    entity: peg
    offset:
    - 0.0
    - 0.03
    - 0.1
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
- id: descend_to_peg
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.03
    - 0.002
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
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
    - 0.03
    - 0.002
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
- **approach_above_peg** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_peg** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, 0.002], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_peg** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, 0.002], offset_along_axis={axis=task_goal_direction, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.234
- **task_score** (E): 0.349
- **fitness_score**: 0.564  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_peg | 1.00 | 1.00 | 0.1345 |
| descend_to_peg | 1.00 | 1.00 | 0.1352 |
| push_peg | 1.00 | 1.00 | 0.1541 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.156, 0.177) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.526 | 3.526 |
| descend_to_peg | descend | 1.00 / step_budget | (0.513, 0.156, 0.177)→(0.500, 0.149, 0.043) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.534 | 0.613 |
| push_peg | push | 1.00 / step_budget | (0.500, 0.149, 0.043)→(0.495, -0.005, 0.037) | (0.503, 0.080, 0.034)→(0.504, -0.033, 0.038) | 0.160→0.049 | 1.00 / 1.333 | 0.485 | 29.605 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.631
- alignment_error: None
- force_efficiency: 0.434
- terminal_score: 0.509
- phase_score: 0.621
- phase_breakdown.push_complete_score: 0.507
- phase_breakdown.reach_peg_score: 0.886

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.576
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.509
- **Median Q (composite search score)**: 0.245
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at upper bound**: push_peg.retry_offset_y
- **Final σ (mean)**: 0.380


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.04972,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_peg.approach_speed":0.0389,"descend_to_peg.descend_speed":0.06147,"push_peg.force_guard_threshold":37.38773,"push_peg.push_distance":0.1609,"push_peg.push_speed":0.05675,"push_peg.retry_offset_y":-0.01611},"optimized_scores":{"best_composite_score":0.24617,"best_fitness_score":0.57617,"best_task_score":0.50944},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":227.0,"contact_point_centroid":[0.49842,0.08455,0.00919],"force_p95":12.33024,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.27799,"mean_force":2.16669,"phase_index":2.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49139,0.1297,0.03737]},{"body_a":"attachment","body_b":"peg","contact_count":107.0,"contact_point_centroid":[0.49547,0.08984,0.04783],"force_p95":18.23709,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.66871,"mean_force":3.59534,"phase_index":2.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49231,0.10122,0.03607]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":25.0,"contact_point_centroid":[0.47468,0.0533,0.04566],"force_p95":8.89279,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.10726,"mean_force":2.37148,"phase_index":2.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49309,0.08406,0.03563]},{"body_a":"peg","body_b":"channel_base_body","contact_count":219.0,"contact_point_centroid":[0.4965,0.119,0.00936],"force_p95":0.71076,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.57719,"phase_index":0.0,"phase_name":"approach_above_peg","phase_type":"approach","tcp_position_centroid":[0.49245,0.1944,0.2358]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_above_peg","phase_type":"approach","tcp_position_centroid":[0.49948,0.19943,0.29746]},{"body_a":"peg","body_b":"channel_base_body","contact_count":462.0,"contact_point_centroid":[0.49613,0.1191,0.00945],"force_p95":0.5975,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63128,"mean_force":0.54007,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48783,0.18852,0.11057]}],"total_contact_groups":6},"final_pose_error":0.0197,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49543,0.01804,0.03967],"final_tcp_position":[0.49485,0.04694,0.03476],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":28.27799,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":244.0,"n_steps_budget":1000.0,"object_pos_end":[0.49599,0.11915,0.03395],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19928,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.53177,"phase_name":"approach_above_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":243.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_peg","tcp_end":[0.48644,0.18994,0.17974],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16235,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":462.0,"n_steps_budget":1000.0,"object_pos_end":[0.49604,0.11897,0.034],"object_pos_start":[0.49599,0.11915,0.03395],"object_to_goal_dist_end":0.1991,"object_to_goal_dist_start":0.19928,"object_z_max":0.03405,"peak_contact_force":0.51107,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":462.0,"raw_peak_contact_force":0.63128,"subtask_id":"reach_peg","tcp_end":[0.49151,0.18789,0.04265],"tcp_start":[0.48644,0.18994,0.17974],"tcp_to_object_dist_end":0.06961,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":354.0,"n_steps_budget":1000.0,"object_pos_end":[0.49543,0.01804,0.03967],"object_pos_start":[0.49604,0.11897,0.034],"object_to_goal_dist_end":0.09814,"object_to_goal_dist_start":0.1991,"object_z_max":0.04294,"peak_contact_force":0.24564,"phase_name":"push_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":359.0,"raw_peak_contact_force":28.27799,"subtask_id":"push_complete","tcp_end":[0.49485,0.04694,0.03476],"tcp_start":[0.49151,0.18789,0.04265],"tcp_to_object_dist_end":0.02932,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.9697,"average_solve_count":198.0,"average_success_count":198.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_peg.approach_speed":0.05668,"descend_to_peg.descend_speed":0.05405,"push_peg.force_guard_threshold":43.676,"push_peg.push_distance":0.17938,"push_peg.push_speed":0.04246,"push_peg.retry_offset_y":-0.00251},"optimized_scores":{"best_composite_score":0.2449,"best_fitness_score":0.5749,"best_task_score":0.31261},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":228.0,"contact_point_centroid":[0.50214,0.02019,0.04776],"force_p95":22.12647,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.12175,"mean_force":6.82558,"phase_index":2.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49722,0.03158,0.03768]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":234.0,"contact_point_centroid":[0.52522,0.005,0.03285],"force_p95":19.37676,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.61802,"mean_force":4.31498,"phase_index":2.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49725,0.03293,0.03769]},{"body_a":"peg","body_b":"channel_base_body","contact_count":206.0,"contact_point_centroid":[0.50641,0.02506,0.0096],"force_p95":17.66513,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.07861,"mean_force":4.31982,"phase_index":2.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49918,0.07322,0.03889]},{"body_a":"peg","body_b":"channel_base_body","contact_count":258.0,"contact_point_centroid":[0.50548,0.06309,0.00933],"force_p95":0.66645,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.59898,"phase_index":0.0,"phase_name":"approach_above_peg","phase_type":"approach","tcp_position_centroid":[0.51139,0.16932,0.23295]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_above_peg","phase_type":"approach","tcp_position_centroid":[0.50047,0.19777,0.29521]},{"body_a":"peg","body_b":"channel_base_body","contact_count":428.0,"contact_point_centroid":[0.50592,0.06295,0.00938],"force_p95":0.5516,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55641,"mean_force":0.54657,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51251,0.13743,0.10936]}],"total_contact_groups":6},"final_pose_error":0.01967,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50749,-0.05484,0.03661],"final_tcp_position":[0.4955,-0.02709,0.0372],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":29.12175,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":286.0,"n_steps_budget":1000.0,"object_pos_end":[0.50603,0.06297,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.5453,"phase_name":"approach_above_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":292.0,"raw_peak_contact_force":3.88411,"subtask_id":"reach_peg","tcp_end":[0.52268,0.14241,0.17597],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1637,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":428.0,"n_steps_budget":1000.0,"object_pos_end":[0.50602,0.06302,0.03381],"object_pos_start":[0.50603,0.06297,0.0338],"object_to_goal_dist_end":0.14328,"object_to_goal_dist_start":0.14323,"object_z_max":0.03381,"peak_contact_force":0.55136,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":428.0,"raw_peak_contact_force":0.55641,"subtask_id":"reach_peg","tcp_end":[0.50404,0.13297,0.04336],"tcp_start":[0.52268,0.14241,0.17597],"tcp_to_object_dist_end":0.07062,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":417.0,"n_steps_budget":1000.0,"object_pos_end":[0.50749,-0.05484,0.03661],"object_pos_start":[0.50602,0.06302,0.03381],"object_to_goal_dist_end":0.02647,"object_to_goal_dist_start":0.14328,"object_z_max":0.03791,"peak_contact_force":0.12264,"phase_name":"push_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":668.0,"raw_peak_contact_force":29.12175,"subtask_id":"push_complete","tcp_end":[0.4955,-0.02709,0.0372],"tcp_start":[0.50404,0.13297,0.04336],"tcp_to_object_dist_end":0.03024,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28144,"average_solve_count":167.0,"average_success_count":167.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_peg.approach_speed":0.06063,"descend_to_peg.descend_speed":0.04143,"push_peg.force_guard_threshold":38.95069,"push_peg.push_distance":0.17983,"push_peg.push_speed":0.09215,"push_peg.retry_offset_y":-0.0},"optimized_scores":{"best_composite_score":0.2106,"best_fitness_score":0.5406,"best_task_score":0.22455},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":193.0,"contact_point_centroid":[0.50186,0.01023,0.04425],"force_p95":19.71429,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.41645,"mean_force":5.23102,"phase_index":2.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49744,0.02159,0.03813]},{"body_a":"peg","body_b":"channel_base_body","contact_count":194.0,"contact_point_centroid":[0.50616,0.01927,0.00963],"force_p95":17.87513,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.50163,"mean_force":5.11847,"phase_index":2.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49972,0.06725,0.03931]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":228.0,"contact_point_centroid":[0.52518,-0.00368,0.02913],"force_p95":6.74382,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.56853,"mean_force":1.5116,"phase_index":2.0,"phase_name":"push_peg","phase_type":"push","tcp_position_centroid":[0.49756,0.02421,0.03816]},{"body_a":"peg","body_b":"channel_base_body","contact_count":265.0,"contact_point_centroid":[0.50562,0.05648,0.00933],"force_p95":0.62731,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.60639,"phase_index":0.0,"phase_name":"approach_above_peg","phase_type":"approach","tcp_position_centroid":[0.51458,0.16614,0.23219]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_above_peg","phase_type":"approach","tcp_position_centroid":[0.50076,0.19729,0.29452]},{"body_a":"peg","body_b":"channel_base_body","contact_count":425.0,"contact_point_centroid":[0.50612,0.05674,0.00938],"force_p95":0.59837,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65016,"mean_force":0.54622,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51598,0.13149,0.10921]}],"total_contact_groups":6},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50779,-0.06085,0.03649],"final_tcp_position":[0.49533,-0.03359,0.03761],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":31.41645,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":294.0,"n_steps_budget":1000.0,"object_pos_end":[0.50612,0.05664,0.03377],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13692,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.50148,"phase_name":"approach_above_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":302.0,"raw_peak_contact_force":4.44541,"subtask_id":"reach_peg","tcp_end":[0.52865,0.13667,0.17513],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.164,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":425.0,"n_steps_budget":1000.0,"object_pos_end":[0.50614,0.0566,0.03378],"object_pos_start":[0.50612,0.05664,0.03377],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.13692,"object_z_max":0.0339,"peak_contact_force":0.54004,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":425.0,"raw_peak_contact_force":0.65016,"subtask_id":"reach_peg","tcp_end":[0.50479,0.12677,0.04362],"tcp_start":[0.52865,0.13667,0.17513],"tcp_to_object_dist_end":0.07088,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":388.0,"n_steps_budget":1000.0,"object_pos_end":[0.50779,-0.06085,0.03649],"object_pos_start":[0.50614,0.0566,0.03378],"object_to_goal_dist_end":0.02097,"object_to_goal_dist_start":0.13688,"object_z_max":0.03785,"peak_contact_force":1.08785,"phase_name":"push_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":615.0,"raw_peak_contact_force":31.41645,"subtask_id":"push_complete","tcp_end":[0.49533,-0.03359,0.03761],"tcp_start":[0.50479,0.12677,0.04362],"tcp_to_object_dist_end":0.02999,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```