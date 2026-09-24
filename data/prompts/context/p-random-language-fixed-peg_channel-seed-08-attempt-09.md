## Search State

- **Seed**: 8
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | -0.2560 | 0.14 | ❌ rejected |
| 8 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | -0.2627 | 0.16 | ✅ accepted |
| 7 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | -0.2676 | 0.15 | ✅ accepted |
| 6 | approach → descend → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | -0.2224 | 0.10 | ✅ accepted |
| 5 | approach → align → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2814 | 0.00 | ❌ rejected |

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

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach | object | (0.00, 0.04, 0.00) | distance | — |
| contact | object | (0.00, 0.02, 0.00) | distance | — |
| push | world | (0.50, -0.08, 0.04) | distance | push_depth |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=-0.256) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: approach
  anchor: object
  offset:
  - 0.0
  - 0.04
  - 0.0
- id: contact
  anchor: object
  offset:
  - 0.0
  - 0.02
  - 0.0
- id: push
  anchor: world
  offset:
  - 0.5
  - -0.08
  - 0.04
phases:
- id: approach_peg
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
    - 0.05
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
  subtask_id: approach
- id: descend_to_object
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
    - 0.025
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
- id: align_and_contact
  type: align
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.01
    - 0.025
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
- id: push_along_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.025
    offset_along_axis:
      distance: 0.18
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
  parameters:
    push_force_limit:
      type: scalar
      range:
      - 10.0
      - 40.0
      default: 30.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    push_lateral_offset:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.005
      binds_to:
      - path: retry.offset.x
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    push_stroke:
      type: scalar
      range:
      - 0.12
      - 0.24
      default: 0.18
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.0
    - 0.0
  subtask_id: push
- id: retract_from_channel
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.15
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.04, 0.05]
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_object** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.04, 0.025]
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **align_and_contact** (`align`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.01, 0.025]
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
- **push_along_channel** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.025], offset_along_axis={axis=channel_axis, distance=0.18, mode=replace_offset_projection, sign=positive}
  - parameter_bindings:
    - push_force_limit: status=consumed; consumers=termination.force_threshold (replace)
    - push_lateral_offset: status=consumed; consumers=retry.offset.x (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_stroke: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.0, 0.0]
- **retract_from_channel** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15]
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.256
- **task_score** (E): 0.143
- **fitness_score**: 0.184  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.2195 |
| descend_to_object | 1.00 | 1.00 | 0.0473 |
| align_and_contact | 1.00 | 1.00 | 0.0143 |
| push_along_channel | 0.00 | 1.00 | 0.0273 |
| retract_from_channel | 1.00 | 1.00 | 0.1223 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.123, 0.097) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.545 | 3.526 |
| descend_to_object | descend | 1.00 / step_budget | (0.513, 0.123, 0.097)→(0.506, 0.121, 0.052) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.667 | 212.140 | 241.828 |
| align_and_contact | align | 1.00 / step_budget | (0.506, 0.121, 0.052)→(0.506, 0.109, 0.046) | (0.503, 0.080, 0.034)→(0.505, 0.076, 0.034) | 0.160→0.157 | 1.00 / 2.333 | 211.190 | 229.403 |
| push_along_channel | push | 0.00 / step_budget | (0.506, 0.109, 0.046)→(0.517, 0.087, 0.057) | (0.505, 0.076, 0.034)→(0.503, 0.042, 0.027) | 0.157→0.123 | 1.00 / 3.000 | 346.780 | 1277.361 |
| retract_from_channel | retract | 1.00 / step_budget | (0.517, 0.087, 0.057)→(0.514, 0.086, 0.179) | (0.503, 0.042, 0.027)→(0.501, 0.042, 0.027) | 0.123→0.123 | 1.00 / 1.000 | 0.623 | 236.383 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.426
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.340
- phase_score: 0.245
- phase_breakdown.push_score: 0.027
- phase_breakdown.approach_score: 0.304
- phase_breakdown.contact_score: 0.839

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.283
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.340
- **Median Q (composite search score)**: -0.285
- **K-run variance**: 0.0052
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.304


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.91176,"average_solve_count":238.0,"average_success_count":238.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_and_contact.align_speed":0.03003,"approach_peg.approach_speed":0.06644,"descend_to_object.descend_speed":0.01801,"push_along_channel.push_lateral_offset":-0.00036,"push_along_channel.push_speed":0.04419,"push_along_channel.push_stroke":0.18447,"retract_from_channel.retract_speed":0.09503},"optimized_scores":{"best_composite_score":-0.15703,"best_fitness_score":0.28297,"best_task_score":0.34031},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":908.0,"contact_point_centroid":[0.48885,0.18391,-8e-05],"force_p95":302.3508,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2606.78061,"mean_force":279.13157,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.5026,0.11889,0.04729]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":13.0,"contact_point_centroid":[0.47484,0.11961,0.02424],"force_p95":2015.12153,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2077.32452,"mean_force":906.24875,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.47649,0.12499,0.01389]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.54704,0.11998,0.05996],"force_p95":694.87362,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":846.99062,"mean_force":437.75168,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49388,0.13522,0.0317]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":169.0,"contact_point_centroid":[0.54295,0.12,0.05998],"force_p95":117.61731,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":125.83905,"mean_force":99.55929,"phase_index":2.0,"phase_name":"align_and_contact","phase_type":"align","tcp_position_centroid":[0.49144,0.1431,0.03485]},{"body_a":"peg","body_b":"channel_base_body","contact_count":961.0,"contact_point_centroid":[0.50106,0.05265,0.00816],"force_p95":0.73742,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":86.59601,"mean_force":0.71524,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50201,0.11936,0.04649]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.49988,0.12693,0.04345],"force_p95":71.50902,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":85.30254,"mean_force":20.84962,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49466,0.13847,0.0348]},{"body_a":"world","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.48949,0.16478,-1e-05],"force_p95":48.28351,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":49.0855,"mean_force":41.06561,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.50564,0.10052,0.04905]},{"body_a":"attachment","body_b":"peg","contact_count":127.0,"contact_point_centroid":[0.49719,0.13204,0.0462],"force_p95":13.5188,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.28123,"mean_force":2.06635,"phase_index":2.0,"phase_name":"align_and_contact","phase_type":"align","tcp_position_centroid":[0.49104,0.1438,0.03488]},{"body_a":"peg","body_b":"channel_base_body","contact_count":224.0,"contact_point_centroid":[0.49936,0.10499,0.0097],"force_p95":11.81468,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.25087,"mean_force":1.62036,"phase_index":2.0,"phase_name":"align_and_contact","phase_type":"align","tcp_position_centroid":[0.49076,0.14585,0.03566]},{"body_a":"peg","body_b":"channel_base_body","contact_count":903.0,"contact_point_centroid":[0.49834,0.05078,0.00805],"force_p95":0.68341,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.81066,"mean_force":0.61351,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.50336,0.09948,0.11815]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.475,0.02777,0.02415],"force_p95":6.82231,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.53556,"mean_force":2.77856,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.50355,0.09973,0.17568]},{"body_a":"peg","body_b":"channel_base_body","contact_count":620.0,"contact_point_centroid":[0.49618,0.11905,0.00944],"force_p95":0.61474,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55171,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49091,0.17956,0.19601]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49946,0.19924,0.29776]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":26.0,"contact_point_centroid":[0.52562,0.09485,0.02117],"force_p95":0.67698,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70507,"mean_force":0.34357,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49642,0.13258,0.03367]},{"body_a":"peg","body_b":"channel_base_body","contact_count":230.0,"contact_point_centroid":[0.49605,0.11933,0.00943],"force_p95":0.59809,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62511,"mean_force":0.54165,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.4855,0.15917,0.07052]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.47498,0.02789,0.02419],"force_p95":0.45142,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45962,"mean_force":0.38327,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.5007,0.13054,0.04716]}],"total_contact_groups":16},"final_pose_error":0.01059,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49564,0.05086,0.02417],"final_tcp_position":[0.50368,0.09982,0.18867],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":2606.78061,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":645.0,"n_steps_budget":1000.0,"object_pos_end":[0.49607,0.11903,0.0338],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19917,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.57334,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":644.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.48374,0.16071,0.0994],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07869,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":230.0,"n_steps_budget":1000.0,"object_pos_end":[0.49604,0.11918,0.03398],"object_pos_start":[0.49607,0.11903,0.0338],"object_to_goal_dist_end":0.19931,"object_to_goal_dist_start":0.19917,"object_z_max":0.03401,"peak_contact_force":0.56259,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":230.0,"raw_peak_contact_force":0.62511,"tcp_end":[0.48985,0.1582,0.04138],"tcp_start":[0.48374,0.16071,0.0994],"tcp_to_object_dist_end":0.0402,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":244.0,"n_steps_budget":660.0,"object_pos_end":[0.50165,0.11024,0.0341],"object_pos_start":[0.49604,0.11918,0.03398],"object_to_goal_dist_end":0.19034,"object_to_goal_dist_start":0.19931,"object_z_max":0.03562,"peak_contact_force":98.102,"phase_name":"align_and_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":520.0,"raw_peak_contact_force":125.83905,"subtask_id":"contact","tcp_end":[0.49311,0.14037,0.03481],"tcp_start":[0.48985,0.1582,0.04138],"tcp_to_object_dist_end":0.03133,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50184,0.05043,0.02413],"object_pos_start":[0.50165,0.11024,0.0341],"object_to_goal_dist_end":0.1314,"object_to_goal_dist_start":0.19034,"object_z_max":0.04088,"peak_contact_force":256.61941,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1940.0,"raw_peak_contact_force":2606.78061,"subtask_id":"push","tcp_end":[0.50564,0.10053,0.04905],"tcp_start":[0.49311,0.14037,0.03481],"tcp_to_object_dist_end":0.05608,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":903.0,"n_steps_budget":990.0,"object_pos_end":[0.49564,0.05086,0.02417],"object_pos_start":[0.50184,0.05043,0.02413],"object_to_goal_dist_end":0.13188,"object_to_goal_dist_start":0.1314,"object_z_max":0.02437,"peak_contact_force":0.64615,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":908.0,"raw_peak_contact_force":49.0855,"tcp_end":[0.50368,0.09982,0.18867],"tcp_start":[0.50564,0.10053,0.04905],"tcp_to_object_dist_end":0.17182,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.06911,"average_solve_count":246.0,"average_success_count":246.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_and_contact.align_speed":0.0348,"approach_peg.approach_speed":0.04577,"descend_to_object.descend_speed":0.03719,"push_along_channel.push_lateral_offset":-0.00389,"push_along_channel.push_speed":0.02434,"push_along_channel.push_stroke":0.19178,"retract_from_channel.retract_speed":0.06467},"optimized_scores":{"best_composite_score":-0.28545,"best_fitness_score":0.15455,"best_task_score":0.08825},"replay_outcomes":[{"contacts":{"omitted_contact_groups":5,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":205.0,"contact_point_centroid":[0.47496,0.11994,0.05075],"force_p95":454.90137,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":531.8001,"mean_force":302.83901,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.51302,0.07927,0.04984]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":90.0,"contact_point_centroid":[0.47499,0.11998,0.05511],"force_p95":417.32376,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":517.71951,"mean_force":80.08163,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.51161,0.08036,0.05548]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":139.0,"contact_point_centroid":[0.52506,0.08106,0.05052],"force_p95":410.30043,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":516.98954,"mean_force":239.43845,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.51239,0.08011,0.04913]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":383.0,"contact_point_centroid":[0.52977,0.11928,0.05998],"force_p95":368.68034,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":432.3862,"mean_force":141.45928,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.5102,0.08041,0.05128]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":183.0,"contact_point_centroid":[0.52508,0.10482,0.05997],"force_p95":339.17352,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":376.97032,"mean_force":325.50926,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.5083,0.10477,0.05149]},{"body_a":"world","body_b":"link7","contact_count":836.0,"contact_point_centroid":[0.49607,0.14463,-7e-05],"force_p95":303.78623,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":343.41412,"mean_force":238.70027,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.51116,0.08073,0.0497]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":425.0,"contact_point_centroid":[0.52504,0.0987,0.05998],"force_p95":286.5501,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":292.65178,"mean_force":234.67075,"phase_index":2.0,"phase_name":"align_and_contact","phase_type":"align","tcp_position_centroid":[0.50408,0.09857,0.04374]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":15.0,"contact_point_centroid":[0.52511,0.08066,0.04983],"force_p95":233.49204,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":257.05978,"mean_force":132.03861,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.51326,0.07963,0.04978]},{"body_a":"world","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.49601,0.14295,-4e-05],"force_p95":175.75071,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":181.25627,"mean_force":137.59844,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.51324,0.07954,0.04973]},{"body_a":"attachment","body_b":"peg","contact_count":22.0,"contact_point_centroid":[0.50552,0.0806,0.04638],"force_p95":4.69481,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.94066,"mean_force":4.38643,"phase_index":2.0,"phase_name":"align_and_contact","phase_type":"align","tcp_position_centroid":[0.50164,0.09251,0.03925]},{"body_a":"peg","body_b":"channel_base_body","contact_count":439.0,"contact_point_centroid":[0.506,0.06184,0.0094],"force_p95":0.55467,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.61793,"mean_force":0.75353,"phase_index":2.0,"phase_name":"align_and_contact","phase_type":"align","tcp_position_centroid":[0.5041,0.0986,0.04377]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.525,0.12,0.06],"force_p95":30.97033,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":31.07018,"mean_force":26.07756,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.5105,0.07853,0.0791]},{"body_a":"attachment","body_b":"peg","contact_count":20.0,"contact_point_centroid":[0.50523,0.07972,0.04904],"force_p95":8.35046,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.77325,"mean_force":1.85481,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50264,0.08789,0.04784]},{"body_a":"peg","body_b":"channel_base_body","contact_count":990.0,"contact_point_centroid":[0.50027,0.02532,0.00838],"force_p95":0.81809,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.8767,"mean_force":0.62918,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.51023,0.08116,0.0506]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":29.0,"contact_point_centroid":[0.52515,0.05117,0.05375],"force_p95":4.23189,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.98431,"mean_force":0.72692,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50583,0.08128,0.05877]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50152,0.01844,0.00805],"force_p95":0.69722,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.96413,"mean_force":0.61081,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.51086,0.07887,0.10847]}],"total_contact_groups":21},"final_pose_error":0.02889,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50166,0.01845,0.02414],"final_tcp_position":[0.51114,0.07879,0.17095],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":531.8001,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":781.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.06301,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14326,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54814,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":787.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach","tcp_end":[0.5243,0.10783,0.09677],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07945,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":322.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.06304,0.0338],"object_pos_start":[0.50593,0.06301,0.0338],"object_to_goal_dist_end":0.1433,"object_to_goal_dist_start":0.14326,"object_z_max":0.03381,"peak_contact_force":333.18001,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":505.0,"raw_peak_contact_force":376.97032,"tcp_end":[0.50715,0.10499,0.04966],"tcp_start":[0.5243,0.10783,0.09677],"tcp_to_object_dist_end":0.04487,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":439.0,"n_steps_budget":660.0,"object_pos_end":[0.50623,0.06204,0.03487],"object_pos_start":[0.50598,0.06304,0.0338],"object_to_goal_dist_end":0.14227,"object_to_goal_dist_start":0.1433,"object_z_max":0.03485,"peak_contact_force":267.34565,"phase_name":"align_and_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":886.0,"raw_peak_contact_force":292.65178,"subtask_id":"contact","tcp_end":[0.50148,0.09183,0.03881],"tcp_start":[0.50715,0.10499,0.04966],"tcp_to_object_dist_end":0.03042,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50102,0.01847,0.02405],"object_pos_start":[0.50623,0.06204,0.03487],"object_to_goal_dist_end":0.09976,"object_to_goal_dist_start":0.14227,"object_z_max":0.04079,"peak_contact_force":531.8001,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2605.0,"raw_peak_contact_force":531.8001,"subtask_id":"push","tcp_end":[0.51321,0.07949,0.04975],"tcp_start":[0.50148,0.09183,0.03881],"tcp_to_object_dist_end":0.06733,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50166,0.01845,0.02414],"object_pos_start":[0.50102,0.01847,0.02405],"object_to_goal_dist_end":0.09973,"object_to_goal_dist_start":0.09976,"object_z_max":0.0245,"peak_contact_force":0.67263,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1122.0,"raw_peak_contact_force":517.71951,"tcp_end":[0.51114,0.07879,0.17095],"tcp_start":[0.51321,0.07949,0.04975],"tcp_to_object_dist_end":0.15901,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.77097,"average_solve_count":310.0,"average_success_count":310.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_and_contact.align_speed":0.02342,"approach_peg.approach_speed":0.08577,"descend_to_object.descend_speed":0.01281,"push_along_channel.push_lateral_offset":0.00053,"push_along_channel.push_speed":0.02979,"push_along_channel.push_stroke":0.16338,"retract_from_channel.retract_speed":0.0363},"optimized_scores":{"best_composite_score":-0.32554,"best_fitness_score":0.11446,"best_task_score":6e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":970.0,"contact_point_centroid":[0.53005,0.09226,0.05992],"force_p95":303.99398,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":693.50354,"mean_force":279.47985,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.53006,0.08622,0.07151]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":883.0,"contact_point_centroid":[0.53078,0.09925,0.0599],"force_p95":323.35856,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":347.88938,"mean_force":317.02175,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.51962,0.09934,0.0642]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":999.0,"contact_point_centroid":[0.53494,0.09778,0.05994],"force_p95":269.36701,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":269.71735,"mean_force":250.00993,"phase_index":2.0,"phase_name":"align_and_contact","phase_type":"align","tcp_position_centroid":[0.52371,0.09799,0.06411]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":33.0,"contact_point_centroid":[0.525,0.11997,0.06],"force_p95":180.12378,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":198.64263,"mean_force":157.59954,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.53068,0.08014,0.07182]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.52678,0.11419,0.05994],"force_p95":127.61349,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":142.34378,"mean_force":68.52465,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.53068,0.08013,0.07189]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":107.0,"contact_point_centroid":[0.525,0.11999,0.05186],"force_p95":47.64693,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":95.69737,"mean_force":23.32926,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.5284,0.0802,0.08152]},{"body_a":"peg","body_b":"channel_base_body","contact_count":717.0,"contact_point_centroid":[0.50596,0.05659,0.00936],"force_p95":0.60057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56867,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51498,0.14903,0.19323]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49994,0.19807,0.29597]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50608,0.05665,0.00938],"force_p95":0.60053,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61062,"mean_force":0.5467,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.52014,0.09943,0.06622]},{"body_a":"peg","body_b":"channel_base_body","contact_count":999.0,"contact_point_centroid":[0.50613,0.05655,0.00939],"force_p95":0.55163,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55679,"mean_force":0.54644,"phase_index":2.0,"phase_name":"align_and_contact","phase_type":"align","tcp_position_centroid":[0.52371,0.09799,0.06411]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.5061,0.05665,0.00939],"force_p95":0.55212,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55444,"mean_force":0.54629,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.53004,0.08638,0.07141]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50619,0.05656,0.00939],"force_p95":0.55308,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55355,"mean_force":0.54628,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.52833,0.0795,0.12298]}],"total_contact_groups":12},"final_pose_error":0.04398,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50601,0.05658,0.03386],"final_tcp_position":[0.52863,0.07948,0.17789],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":693.50354,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":746.0,"n_steps_budget":1000.0,"object_pos_end":[0.50612,0.05663,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.51391,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":754.0,"raw_peak_contact_force":4.44541,"subtask_id":"approach","tcp_end":[0.53082,0.10166,0.09618],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08082,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50616,0.05663,0.0338],"object_pos_start":[0.50612,0.05663,0.03378],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.13691,"object_z_max":0.0338,"peak_contact_force":302.67603,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1883.0,"raw_peak_contact_force":347.88938,"tcp_end":[0.52248,0.09984,0.0641],"tcp_start":[0.53082,0.10166,0.09618],"tcp_to_object_dist_end":0.05524,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":999.0,"n_steps_budget":1000.0,"object_pos_end":[0.50605,0.05667,0.03385],"object_pos_start":[0.50616,0.05663,0.0338],"object_to_goal_dist_end":0.13694,"object_to_goal_dist_start":0.13691,"object_z_max":0.03385,"peak_contact_force":268.12117,"phase_name":"align_and_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1998.0,"raw_peak_contact_force":269.71735,"subtask_id":"contact","tcp_end":[0.52455,0.09461,0.06409],"tcp_start":[0.52248,0.09984,0.0641],"tcp_to_object_dist_end":0.05192,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50616,0.05672,0.03386],"object_pos_start":[0.50605,0.05667,0.03385],"object_to_goal_dist_end":0.13699,"object_to_goal_dist_start":0.13694,"object_z_max":0.03386,"peak_contact_force":251.91903,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2003.0,"raw_peak_contact_force":693.50354,"subtask_id":"push","tcp_end":[0.53071,0.08011,0.07182],"tcp_start":[0.52455,0.09461,0.06409],"tcp_to_object_dist_end":0.0509,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50601,0.05658,0.03386],"object_pos_start":[0.50616,0.05672,0.03386],"object_to_goal_dist_end":0.13685,"object_to_goal_dist_start":0.13699,"object_z_max":0.03386,"peak_contact_force":0.54873,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1114.0,"raw_peak_contact_force":142.34378,"tcp_end":[0.52863,0.07948,0.17789],"tcp_start":[0.53071,0.08011,0.07182],"tcp_to_object_dist_end":0.14758,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```